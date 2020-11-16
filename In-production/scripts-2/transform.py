import sys
from collections import defaultdict
import glob
import os
import xlsxwriter
import vcf
import functions


def create_report_file(variants_files, outfile):

    formatted_lines = {'small_mutations': [], 'fusions': [], 'cnvs': []}
    for file in variants_files:
        sample_name, variant_info = read_variants_file(file)
        print ('SAMPLE NAME', sample_name)

        lims_data = functions.get_record_info_limsapi(sample_name)

        # Format variants
        functions.get_interpretations(variant_info, lims_data)
        variants = _sort_variants(variant_info)
        fusions = _format_fusions(variants['fusions'])
        small_mutations = _format_small_mutations(variants['small_mutations'])
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
        sample_name = os.path.basename(filename)
        sample_name = sample_name.split("_")
        sample_name = sample_name[0]
        
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

    fields = {
        'Genes': func.get('gene'),
        'Type': record['INFO']['TYPE'][which_alt].upper(),
        'Coding': func.get('coding'),
        'Amino Acid Change': func.get('protein'),
        'Phred QUAL Score': record['QUAL'],
        'Variant ID': ';'.join(record['ID']),
        'Coverage': record['INFO'].get('DP'),
        'Oncomine Gene Class': func.get('oncomineGeneClass'),
        'Frequency': record['INFO']['AF'][which_alt],
        'Strand Bias': record['INFO']['STB'][which_alt],
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
        'Chrom': record['CHROM'],
        'Pos': record['POS'],
        'Genes': '{}({}) - {}({})'.format(func1.get('gene'), func1.get('exon'), func2.get('gene'), func2.get('exon')),
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


def _format_small_mutations(variants):
    small_mutation_fields = []
    for variant in variants:
        # if _small_mutation_passes_filter(variant):
        try:
            mutation = '{} {}, {}'.format(variant['Genes'], 
                                          variant['Coding'], 
                                          variant['Amino Acid Change'])
            fields = _format_common_fields(variant)
            fields.update({
                'Sample Avg. Coverage': '',
                'Mutation': mutation,
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
            decoded_field = str(field).decode('utf-8')
            worksheet.write_string(row+1, col, decoded_field)


if __name__ == '__main__':
    
    infolder = sys.argv[1]
    outfile = sys.argv[2]

    infiles = glob.glob('{}/*.vcf'.format(infolder))
    create_report_file(infiles, outfile)
