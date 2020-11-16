import sys, os
from collections import defaultdict
import glob
import xlrd, xlsxwriter, xlwt
from xlutils.copy import copy
import vcf
import functions


###I added this function to parse additional VCF ANNOTATION
def extended_Annotations(in_vcf,outfile):
    #Open the annotated vcf to grep lines on CDOT
    if in_vcf.endswith('.gz'):
        vcf=gzip.open(in_vcf,'r+')
    else:
        vcf=open(in_vcf,'r+')
    lines = vcf.readlines()
    #Open worksheet
    outname2 = str(outfile+'.extendedAnn.xls')
    w = xlrd.open_workbook(outfile)
    sheet = w.sheet_by_index(0) #The SNVs
    #Now loop through the 'Mutation' column to grep on CDOT notation
    Mutations = sheet.col_values(13)
    ExAC_AF_l = []
    ThousG_AF_l = []
    clinvar_rs_l = []
    for row in Mutations[1:]: #Skipping the header
        x = row.split()
        CDOT = str(x[1]).replace(',','')
        match_l = [line for line in lines if CDOT in line]
        fields = match_l[0].split()[-3] #The annotations fields -- aka INFO
        ExAC_AF = [item.split('=')[-1] for item in fields.split(';') if item.startswith('dbNSFP_ExAC_AF=')]
        ThousG_AF = [item.split('=')[-1] for item in fields.split(';') if item.startswith('dbNSFP_1000Gp3_AF=')]
        clinvar_rs = [item.split('=')[-1] for item in fields.split(';') if item.startswith('dbNSFP_clinvar_rs=')]
        if ExAC_AF:
            ExAC_AF_l.append(ExAC_AF)
        else:
            ExAC_AF_l.append('.')
        if ThousG_AF:
            ThousG_AF_l.append(ThousG_AF)
        else:
            ThousG_AF_l.append('.')
        if clinvar_rs:
            clinvar_rs_l.append(clinvar_rs)
        else:
            clinvar_rs_l.append('.')
    #Now write the results for the SNVs to the new sheet2
    w2 = copy(xlrd.open_workbook(outfile))
    sheet2 = w2.get_sheet(0)
    sheet2.write(0,27,'ExAC_AF')
    sheet2.write(0,28,'1000G_AF')
    sheet2.write(0,29,'clinvar_rs')
    row=1
    for l in ExAC_AF_l:
        sheet2.write(row,27,l)
        row +=1
    row=1
    for l in ThousG_AF_l:
        sheet2.write(row,28,l)
        row +=1
    row=1
    for l in clinvar_rs_l:
        sheet2.write(row,29,l)
        row +=1

    w2.save(outname2)


#Add function to run PertinentNegatives module and pull results into new tab of xlsx
def PertinentNegatives(PertNegBook,outfile):
    PertNeg = open(PertNegBook,'r+')
    linet = PertNeg.readlines()
    SampleID = [x.split('\t')[2] for x in linet]
    Mutation = [x.split('\t')[11] for x in linet]
    Frequency = [x.split('\t')[15] for x in linet]
    TotalCoverage = [x.split('\t')[18] for x in linet]
    w = xlrd.open_workbook(outfile)
    w2 = copy(w)
    P_Sheet = w2.add_sheet('Pertinent Negatives')
    #And write the lines
    P_Sheet.write(0,0,'Patient Name')
    P_Sheet.write(0,1,'Accession #')
    P_Sheet.write(0,3,'DNA Barcode')
    P_Sheet.write(0,4,'RNA Barcode')
    P_Sheet.write(0,5,'Surgical Path #')
    P_Sheet.write(0,6,'Tumor')
    P_Sheet.write(0,7,'Primary Site')
    P_Sheet.write(0,8,'Block')
    P_Sheet.write(0,9,'Cellularity')
    P_Sheet.write(0,10,'Sample Avg. Coverage')
    P_Sheet.write(0,12,'Type')
    P_Sheet.write(0,13,'Oncomine Gene Class')
    P_Sheet.write(0,14,'Tier')
    P_Sheet.write(0,16,'Quality')
    P_Sheet.write(0,17,'COSMIC ID')
    P_Sheet.write(0,19,'Exon')
    P_Sheet.write(0,20,'Strand Bias')
    P_Sheet.write(0,21,'Exclude')
    P_Sheet.write(0,22,'Warnings')
    P_Sheet.write(0,23,'Interpretation')
    P_Sheet.write(0,24,'Citations')
    P_Sheet.write(0,25,'ExAC_AF')
    P_Sheet.write(0,26,'1000G_AF')
    P_Sheet.write(0,27,'clinvar_rs')
    row = 0
    for l in range(0,len(SampleID)):
        P_Sheet.write(row,2,SampleID[l])
        P_Sheet.write(row,11,Mutation[l])
        P_Sheet.write(row,15,Frequency[l])
        P_Sheet.write(row,18,TotalCoverage[l])
        row +=1
    w2.save(outfile)

def create_report_file(variants_files, outfile):

    # Get information from variants file (from Ion Reporter)
    formatted_lines = {'small_mutations': [], 'fusions': [], 'cnvs': []}
    for file in variants_files:
        sample_name, variant_info = read_variants_file(file)
        print("SAMPLE NAME: {}".format(sample_name))
        sampleID = sample_name.split("_")
        print("SAMPLE ID: {}".format(sampleID[0]))
        global ann_name
        ann_name = file.split('.vcf')[0]+'.ann.vcf'
        print('Reading annotated vcf {}...'.format(ann_name))

        lims_data = functions.get_record_info_limsapi(sampleID[0])

        # Format variants #Comment out line 47 if PMKB times out
        functions.get_interpretations(variant_info, lims_data)
        variants = _sort_variants(variant_info)
        fusions = _format_fusions(variants['fusions'])
        small_mutations = _format_small_mutations(variants['small_mutations'],True)
        cnvs = _format_cnvs(variants['cnvs'])

        _format_lines(
            formatted_lines, lims_data, small_mutations, fusions, cnvs
        )

    write_excel(outfile, formatted_lines)


def read_variants_file(filename):
    print ('Reading results file {}...'.format(filename))

    sample_name = ''
    entries = []
    fusion_count = 0
    with open(filename, 'r') as file:
        vcf_info = vcf.read_vcf(file, filename)
        sample_name = vcf_info.headers[-1]
        for index, record in enumerate(vcf_info.records):
            which_alt = None
            vtype = record['INFO'].get('SVTYPE')

            if vtype is None:
                alle1, alle2 = record[sample_name]['GT'].split('/')
                if alle1 not in ['0', '.']:
                    which_alt = int(alle1)-1
                elif alle2 not in ['0', '.']:
                    which_alt = int(alle2)-1
                else:
                    continue
                vtype = record['INFO']['TYPE'][which_alt].upper()

            entry = {}
            if vtype == 'CNV':
                entry = _read_cnv_record(record, sample_name)
            elif vtype == 'Fusion' or vtype == 'RNAExonVariant':
                if record['FILTER'] == 'PASS':
                    fusion_count = fusion_count + 1
                    if fusion_count == 2:
                        entry = _read_fusion_record(record, sample_name, vcf_info.records, index)
                        fusion_count = 0
            elif vtype not in [None, '5p3pAssays', 'ExprControl','RNAExonVariant']:
                entry = _read_record(record, sample_name, which_alt)
            else:
                continue
            if entry:
                entries.append(entry)

    return [sample_name, entries]


def _read_cnv_record(record, sample_name):
    fields = {
        'Type': record['INFO'].get('SVTYPE'),
        'Genes': record['INFO']['FUNC'][0].get('gene'),
        'Chrom': record['CHROM'],
        'Pos': record['POS'],
        'Oncomine Variant Class': record['INFO']['FUNC'][0].get('oncomineVariantClass'),
        'Copy Number': record['INFO'].get('RAW_CN'),
        'CytoBand': '',
        'CNV Confidence': (', ').join(record['INFO']['CI']),
        'Oncomine Gene Class': record['INFO']['FUNC'][0].get('oncomineGeneClass')
    }
    return fields


def _read_record(record, sample_name, which_alt):
    func = record['INFO']['FUNC'][0]
    
    if func.get('protein') is None or '=' in func.get('protein'):
        return {}

    fields = {}
    if 'STB' in record['INFO']: 
        fields = {        
            'Genes': func.get('gene'),
            'Type': record['INFO']['TYPE'][which_alt].upper(),
            'Coding': func.get('coding'),
            'Chrom': record['CHROM'],
            'Pos': record['POS'],
            'Amino Acid Change': func.get('protein'),
            'Phred QUAL Score': record['QUAL'],
            'Variant ID': ';'.join(record['ID']),
            'Coverage': record['INFO'].get('DP'),
            'Oncomine Gene Class': func.get('oncomineGeneClass'),
            'Frequency': record['INFO']['AF'][which_alt],
            'Strand Bias': record['INFO']['STB'][which_alt],
            'Exon': func.get('exon')
    }
    else:
        fields = {
            'Genes': func.get('gene'),
            'Type': record['INFO']['TYPE'][which_alt].upper(),
            'Coding': func.get('coding'),
            'Chrom': record['CHROM'],
            'Pos': record['POS'], 
            'Amino Acid Change': func.get('protein'),
            'Phred QUAL Score': record['QUAL'],
            'Variant ID': ';'.join(record['ID']),
            'Coverage': record['INFO'].get('DP'),
            'Oncomine Gene Class': func.get('oncomineGeneClass'),
            'Frequency': record['INFO']['AF'][which_alt],
            'Strand Bias': '',
            'Exon': func.get('exon')
    }
    
    return fields


def _read_fusion_record(record, sample_name, all_records, index):
    
    record = all_records[index-1]
    record2 = all_records[index]
    
    func1 = record['INFO']['FUNC'][0]
    func2 = record2['INFO']['FUNC'][0]

    fields = {
        'Type': record['INFO'].get('SVTYPE'),
        'Genes': '{}({}) - {}({})'.format(func1.get('gene'), func1.get('exon'), func2.get('gene'), func2.get('exon')),
        'Chrom': record['CHROM'],
        'Pos': record['POS'],
        'Read Counts': record['INFO']['READ_COUNT'][0],
        'Read Counts Per Million': record['INFO']['RPM'][0],
        'COSMIC/NCBI': record['INFO'].get('ANNOTATION'),
        'Oncomine Gene Class': func1.get('oncomineGeneClass')
    }

    return fields


def _sort_variants(entries):
    results = {
        'fusions': [],
        'small_mutations': [],
        'cnvs': []
    }
    for entry in entries:
        typ = entry['Type']
        if typ == 'Fusion' or typ == 'RNAExonVariant':
            results['fusions'].append(entry)
        elif typ == 'CNV':
            results['cnvs'].append(entry)
        elif typ:
            results['small_mutations'].append(entry)
    return results


def _format_common_fields(variant):
    fields_dict = defaultdict(lambda: '')
    fields_dict['Genes'] = variant['Genes']
    fields_dict['Type'] = variant['Type']

    if variant.get('Interpretation') is not None:
        fields_dict['Interpretation'] = variant['Interpretation'].encode('utf-8')
        fields_dict['Citations'] = '|'.join(
            map(lambda x: x['citation'], variant['Citations'])
        ).encode('utf-8')
        fields_dict['Tier'] = variant['Tier']

    return fields_dict


def _format_small_mutations(variants,add_annotations):
    small_mutation_fields = []
    for variant in variants:
        try:
            mutation = '{} {}, {}'.format(variant['Genes'],
                                          variant['Coding'],
                                          variant['Amino Acid Change'])
            fields = _format_common_fields(variant)
            fields.update({
                'Sample Avg. Coverage': '',
                'Genes': str(variant['Genes']),
                'Mutation': mutation,
                'Chromosome Position': "{}:{}".format(variant['Chrom'], variant['Pos']),
                'Frequency': str(variant['Frequency'] * 100) + '%',
                'Quality': variant['Phred QUAL Score'],
                'COSMIC ID': variant['Variant ID'],
                'Total Coverage': variant['Coverage'],
                'Oncomine Gene Class': variant['Oncomine Gene Class'],
                'Strand Bias': variant['Strand Bias'],
                'Exon': variant['Exon'],
                'Type': variant['Type'].replace('SNP', 'SNV')
            })
            small_mutation_fields.append(fields)
        except Exception as e:
            print(e)
            print(variant)
            continue

    return small_mutation_fields


def _small_mutation_passes_filter(variant):
    if variant['Frequency'] < 0.03:
        return False
    elif variant['Frequency'] < 0.05 and variant['Coverage'] < 1000:
        return False
    elif variant['Coverage'] < 400:
        return False
    return True


def _format_fusions(variants):
    fusion_fields = []

    for variant in variants:
        fields = _format_common_fields(variant)
        fields.update({
            'Read Counts': variant['Read Counts'],
            'Chromosome Position': "{}:{}".format(variant['Chrom'], variant['Pos']),
            'Read Counts Per Million': variant['Read Counts Per Million'],
            'COSMIC ID': variant['COSMIC/NCBI'],
            'Oncomine Gene Class': variant['Oncomine Gene Class']
        })
        fusion_fields.append(fields)
    return fusion_fields


def _format_cnvs(variants):
    cnv_fields = []
    for variant in variants:
        fields = _format_common_fields(variant)
        fields.update({
            'CNV Type': variant['Oncomine Variant Class'],
            'Chromosome Position': "{}:{}".format(variant['Chrom'], variant['Pos']),
            'Copy Number': variant['Copy Number'],
            'Cytoband': variant['CytoBand'],
            'CNV Confidence': variant['CNV Confidence'],
            'Oncomine Gene Class': variant['Oncomine Gene Class']
        })
        cnv_fields.append(fields)
    return cnv_fields


def _sample_headers():
    return [
        'Patient Name',
        'Accession #',
        'Sample ID',
        'DNA Barcode',
        'RNA Barcode',
        'Surgical Path #',
        'Tumor',
        'Primary Site',
        'Block',
        'Cellularity',
        'Sample Avg. Coverage'
    ]


def _small_mutation_headers():
    return [
        'Genes',
        'Chromosome Position',
        'Mutation',
        'Type',
        'Oncomine Gene Class',
        'Tier',
        'Frequency',
        'Quality',
        'COSMIC ID',
        'Total Coverage',
        'Exon',
        'Strand Bias',
        'Exclude',
        'Warnings',
        'Interpretation',
        'Citations',
    ]


####Added This for additional annotations!
def _small_mutation_headers_extended():
    return [
        'Genes',
        'Chromosome Position',
        'Mutation',
        'Type',
        'Oncomine Gene Class',
        'Tier',
        'Frequency',
        'Quality',
        'COSMIC ID',
        'ExAC AF',
        '1000G AF',
        'Total Coverage',
        'Exon',
        'Strand Bias',
        'Exclude',
        'Warnings',
        'Interpretation',
        'Citations',
    ]


def _fusion_headers():
    return [
        'Genes',
        'Chromosome Position',
        'Type',
        'Oncomine Gene Class',
        'Tier',
        'Read Counts',
        'Read Counts Per Million',
        'COSMIC ID',
        'Exclude',
        'Warnings',
        'Interpretation',
        'Citations',
    ]


def _cnv_headers():
    return [
        'Genes',
        'Chromosome Position',
        'Type',
        'Oncomine Gene Class',
        'Tier',
        'CNV Type',
        'Copy Number',
        'Cytoband',
        'CNV Confidence',
        'Exclude',
        'Warnings',
        'Interpretation',
        'Citations'
    ]


def _get_column_width(column):
    widths = {
        'Mutation': 35,
        'Sample ID': 30,
        'Genes': 25,
        'Cytoband': 35
    }
    width = widths.get(column)
    if width is None:
        return 10
    return width


def _format_lines(formatted_lines, sample_fields, small_mutations, fusions, cnvs):
    formatted_variants = _format_worksheet_lines(_small_mutation_headers(),
                                                 sample_fields,
                                                 small_mutations)
    formatted_fusions = _format_worksheet_lines(_fusion_headers(),
                                                sample_fields,
                                                fusions)
    formatted_cnvs = _format_worksheet_lines(_cnv_headers(),
                                             sample_fields,
                                             cnvs)
    formatted_lines['small_mutations'] += formatted_variants
    formatted_lines['fusions'] += formatted_fusions
    formatted_lines['cnvs'] += formatted_cnvs


def _format_worksheet_lines(headers, sample_fields, variants):
    lines = []
    sample_headers = _sample_headers() 
    for variant in variants:
        line = []
        for header in sample_headers:
            if header == 'Patient Name':
                line.append(sample_fields['Name'])
            elif header == 'Sample ID':
                line.append(sample_fields['SampleId'])
            elif header == 'DNA Barcode':
                line.append(sample_fields['DNABarcode'])
            elif header == 'RNA Barcode':
                line.append(sample_fields['RNABarcode'])
            elif header == 'Surgical Path #':
                line.append(sample_fields['PathologyId'])
            elif header == 'Tumor':
                line.append(sample_fields['TumorType'])
            elif header == 'Primary Site':
                line.append(sample_fields['PrimarySite'])
            elif header == 'Cellularity':
                line.append(sample_fields['TumorPercent'])
            else:
                line.append('NA')

        for header in headers:
            line.append(variant[header])
        lines.append(line)
    return lines


def write_excel(outfile, formatted_lines):
    print ('Writing {}...'.format(outfile))

    workbook = xlsxwriter.Workbook(outfile)

    small_mutations_worksheet = workbook.add_worksheet('Variants')
    fusions_worksheet = workbook.add_worksheet('Fusions')
    cnvs_worksheet = workbook.add_worksheet('CNVs')

    _write_excel_worksheet(small_mutations_worksheet,
                           _small_mutation_headers(),
                           formatted_lines['small_mutations'])
    _write_excel_worksheet(fusions_worksheet,
                           _fusion_headers(),
                           formatted_lines['fusions'])
    _write_excel_worksheet(cnvs_worksheet,
                           _cnv_headers(),
                           formatted_lines['cnvs'])

    print ('File successfully written.')


def _write_excel_worksheet(worksheet, headers, lines):
    sample_headers = _sample_headers()
    sample_headers_length = len(sample_headers)

    for col, header in enumerate(sample_headers):
        worksheet.write(0, col, header)
        worksheet.set_column(col, col, _get_column_width(header))

    for relcol, header in enumerate(headers):
        actcol = sample_headers_length + relcol
        worksheet.write(0, actcol, header)
        worksheet.set_column(actcol, actcol, _get_column_width(header))

    for row, line in enumerate(lines):
        for col, field in enumerate(line):
            if col == 11:
                decoded_field = str(field).decode('utf-8')
                worksheet.write_url(row+1, col, 'http://tumorportal.org/view?geneSymbol='+decoded_field, string=decoded_field)
            else:
                decoded_field = str(field).decode('utf-8')
                worksheet.write_string(row+1, col, decoded_field)


if __name__ == '__main__':
    infolder = sys.argv[1]
    outfile = sys.argv[2]

    infiles = glob.glob('{}/*v1.vcf'.format(infolder))
    create_report_file(infiles, outfile)

    add_annotations = True
    add_pertinent_negatives = True
    if add_annotations:
        in_vcf = glob.glob('{}/*ann.vcf'.format(infolder))
        print ('Writing extended annotations {}...'.format(str(outfile+'.extendedAnn.xls')))
        extended_Annotations(in_vcf[0],outfile)
    if add_pertinent_negatives:
        negbook_default = glob.glob('{}/*.PertinentNegatives.xls'.format(infolder))
        print('Adding pertinent negatives tab {}...'.format(str(outfile+'.extendedAnn.xls')))
        PertinentNegatives(negbook_default[0],str(outfile+'.extendedAnn.xls'))