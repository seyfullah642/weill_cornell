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

    localhost = config.CONFIG_PATHS['localhost']
    pmbam = config.CONFIG_PATHS['pmbam']

    absPath = os.path.dirname(excel)
    sampName = excel.split('.')
    sampleName = sampName[0].split("_")
    output = os.path.join(absPath, sampName[0]+"_final.xlsx")

    xlworkbook = xlrd.open_workbook(excel)
    variantSheet = xlworkbook.sheet_by_index(0)
    
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

    cnvSheet = xlworkbook.sheet_by_index(2)

    workbook = xlsxwriter.Workbook(output)
    variant_worksheet = workbook.add_worksheet('Variants')
    
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


    cnv_worksheet = workbook.add_worksheet('CNVs')

    for row in range(variantSheet.nrows):
        #print(variantSheet.row_values(row))
        for col, line in enumerate(variantSheet.row_values(row)):
            variant_worksheet.write(row, col, line)

    for row in range(cnvSheet.nrows):
        for col, line in enumerate(cnvSheet.row_values(row)):
            cnv_worksheet.write(row, col, line)

if __name__ == '__main__':
  main()
