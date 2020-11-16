#!/usr/bin/env python2

import sys
import xlrd
import re
import xlsxwriter
import os
import re
import config

def main():

    excel = sys.argv[1]
    runNum = sys.argv[2]
    ensembl_file = sys.argv[3]

    localhost = config.CONFIG_PATHS['localhost']
    pmbam = config.CONFIG_PATHS['pmbam']
    
    geneEnsembl = {}
    ensembl = open(ensembl_file,"r")
    data = ensembl.read().splitlines()

    for i in data:
        info = i.split("\t")
        geneEnsembl[info[0]] = info[1]

    absPath = os.path.dirname(excel)
    print(absPath)
    sampName = excel.split('.')
    sampleName = sampName[0].split("_")
    output = os.path.join(absPath, sampName[0]+"_final.xlsx")

    xlworkbook = xlrd.open_workbook(excel)
    
    variantSheet = xlworkbook.sheet_by_index(0)
    variant_data = []
    variant_headers = []
    for ncol in xrange(0, variantSheet.ncols):
        variant_headers.append(variantSheet.cell_value(0, ncol))
    for nrow in xrange(1, variantSheet.nrows):
        row = {}
        for ncol, header in enumerate(variant_headers):
            row[header] = variantSheet.cell_value(nrow, ncol)
        variant_data.append(row)

    fusionSheet = xlworkbook.sheet_by_index(1)
    fusion_data = []
    fusion_headers = []
    for ncol in xrange(0, fusionSheet.ncols):
        fusion_headers.append(fusionSheet.cell_value(0, ncol))
    for nrow in xrange(1, fusionSheet.nrows):
        row = {}
        for ncol, header in enumerate(fusion_headers):
            row[header] = fusionSheet.cell_value(nrow, ncol)
        fusion_data.append(row)
    
    #print(fusion_data)

    cnvSheet = xlworkbook.sheet_by_index(2)
    cnv_data = []
    cnv_headers = []
    for ncol in xrange(0, cnvSheet.ncols):
        cnv_headers.append(cnvSheet.cell_value(0, ncol))
    for nrow in xrange(1, cnvSheet.nrows):
        row = {}
        for ncol, header in enumerate(cnv_headers):
            row[header] = cnvSheet.cell_value(nrow, ncol)
        cnv_data.append(row)
    
    #print(cnv_data)

    pnSheet = xlworkbook.sheet_by_index(3)

    workbook = xlsxwriter.Workbook(output)
    
    #Variants
    variant_worksheet = workbook.add_worksheet('Variants')
    for col, header in enumerate(variant_headers):
        variant_worksheet.write(0, col, header)
    
    variant_worksheet.write(0, 30, "Oncokb")
    variant_worksheet.write(0, 31, "Ensembl")
    variant_worksheet.write(0, 32, "gnomAD")
    variant_worksheet.write(0, 33, "ClinVar")
    
    for row, variant in enumerate(variant_data):
        #print(variant)
        for col, line in enumerate(variant_headers):
            if line == "Tier" and variant[line] == '':
                variant[line] = "3"
                variant_worksheet.write(row+1,col, variant[line])
            if line == "Chromosome Position":
                variant_worksheet.write_url(row+1, col, "{}{}".format(localhost, str(variant[line])), string=str(variant[line]))
            if line == "Genes":
                variant_worksheet.write_url(row+1, col, "http://tumorportal.org/view?geneSymbol={}".format(variant[line]), string=variant[line])
                variant_worksheet.write_url(row+1, 30, "http://oncokb.org/#/gene/{}".format(variant[line]))
                variant_worksheet.write_url(row+1, 31, "http://grch37.ensembl.org/Human/Search/Results?q={};site=ensembl;facet_species=Human".format(variant[line]))
                variant_worksheet.write_url(row+1, 32, "http://gnomad.broadinstitute.org/gene/"+geneEnsembl[variant[line]])
                variant_worksheet.write_url(row+1, 33, "https://www.ncbi.nlm.nih.gov/clinvar/?term={}%5Bgene%5D".format(variant[line]))
            if line == "Mutation" and re.search(r",\sp\.\?",variant[line]) and variant['COSMIC ID'] == ".":
                variant_worksheet.write(row+1, 23, "exclude")

            variant_worksheet.write(row+1,col, variant[line])

    variant_worksheet.write(variantSheet.nrows+2, 0, "PMBAM")
    variant_worksheet.write_url(variantSheet.nrows+3, 0, "{}/{}/bam/{}.rawlib.bam".format(pmbam,runNum,sampleName[0]))

    #Fusions
    fusion_worksheet = workbook.add_worksheet('Fusions')
    
    for col, header in enumerate(fusion_headers):
        fusion_worksheet.write(0, col, header)
    
    for row, fusion in enumerate(fusion_data):
        #print(fusion)
        for col, line in enumerate(fusion_headers):
            if line == "Tier" and fusion[line] == '':
                fusion[line] = "3"
            if line == "Chromosome Position":
                fusion_worksheet.write_url(row+1, col, "{}{}".format(localhost, str(fusion[line])), string=str(fusion[line]))
            
            fusion_worksheet.write(row+1, col, fusion[line])
    
    fusion_worksheet.write(fusionSheet.nrows+2, 0, "PMBAM")
    fusion_worksheet.write(fusionSheet.nrows+3, 0, "{}/{}/bam/{}.rawlib.basecaller.bam".format(pmbam, runNum, sampleName[0]))

    #CNVs
    cnv_worksheet = workbook.add_worksheet('CNVs')
    for col, header in enumerate(cnv_headers):
        cnv_worksheet.write(0, col, header)
    
    cnv_worksheet.write(0, 24, "Oncokb")
    cnv_worksheet.write(0, 25, "Ensembl")
    cnv_worksheet.write(0, 26, "gnomAD")
    cnv_worksheet.write(0, 27, "ClinVar")

    for row, cnv in enumerate(cnv_data):
        #print(cnv)
        for col, line in enumerate(cnv_headers):
            if line == "Tier" and cnv[line] == '':
                cnv[line] = "3"
            if line == "Chromosome Position":
                cnv_worksheet.write_url(row+1, col, "{}{}".format(localhost, str(cnv[line])), string=str(cnv[line]))
            if line == "Copy Number":
                copyNum = cnv[line]
                copyNum = float(copyNum)
                if copyNum > 0 and copyNum < 4:
                    cnv_worksheet.write(row+1, 20, "exclude")

            if line == "Genes":
                cnv_worksheet.write_url(row+1, col, "http://tumorportal.org/view?geneSymbol={}".format(cnv[line]), string=cnv[line])
                cnv_worksheet.write_url(row+1, 24, "http://oncokb.org/#/gene/{}".format(cnv[line]))
                cnv_worksheet.write_url(row+1, 25, "http://grch37.ensembl.org/Human/Search/Results?q={};site=ensembl;facet_species=Human".format(cnv[line]))
                cnv_worksheet.write_url(row+1, 26, "http://gnomad.broadinstitute.org/gene/"+geneEnsembl[cnv[line]])
                cnv_worksheet.write_url(row+1, 27, "https://www.ncbi.nlm.nih.gov/clinvar/?term={}%5Bgene%5D".format(cnv[line]))
            
            cnv_worksheet.write(row+1, col, cnv[line])

    #Pertinent Negatives
    pn_worksheet = workbook.add_worksheet('Pertinent Negatives')

    for row in range(pnSheet.nrows):
        for col, line in enumerate(pnSheet.row_values(row)):
            pn_worksheet.write(row, col, line)

if __name__ == '__main__':
  main()
