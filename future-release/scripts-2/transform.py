import sys
import json
from collections import defaultdict
import glob
import os
import requests
from requests.adapters import HTTPAdapter
import xlsxwriter
import config
import vcf
from functions import create_dummy_json

def create_report_file(variants_files, outfile):

    formatted_lines = {'small_mutations': [], 'fusions': [], 'cnvs': []}
    for file in variants_files:
        sample_name, variant_info = read_variants_file(file)
        print ('SAMPLE NAME', sample_name)

        lims_data = get_record_info_limsapi(sample_name)

        # Format variants
        _get_interpretations(variant_info, lims_data)
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

def get_record_info_limsapi(sampleName):
    print ('Pulling data from lims for {}...'.format(sampleName))

    limsUsername = config.CONFIG_PATHS['limsUsername']
    limsPassword = config.CONFIG_PATHS['limsPassword']
    pmauth = config.CONFIG_PATHS['pmauth']
    limsapi = config.CONFIG_PATHS['limsapi']

    auth_url = pmauth
    token_headers = {'content-type':'application/json'}
    token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

    token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
    token = token_req.json()

    print("Token request status code:")
    print(token_req.status_code)
    
    #Get entire oncorseq spreadsheet or by just sample GET IS TO GET AN ENTRY
    sample_url = "{}/{}".format(limsapi,sampleName)
    sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
    sample_req = requests.get(sample_url, headers=sample_headers)
    sample_record = sample_req.json()

    return sample_record['dataRecords'][0]['fields']

def _get_interpretations(variants, sample_fields):
    # Format params dict to send to PMKB
    collected_params = []
    for variant in variants:
        params = {
            'tumor': sample_fields['TumorType'],
            'tissue': sample_fields['PrimarySite']
        }
        if variant['Type'] == 'Fusion':
            gene1 = variant['Genes'].split('(')[0]
            gene2 = variant['Genes'].split('-')[1].lstrip().split('(')[0]

            params['variant_type'] = 'rearrangement'
            params['gene'] = gene2

            params['partner_gene'] = gene1

        elif variant['Type'] == 'CNV':
            cnv_type = 'any'
            if variant['Oncomine Variant Class'] == 'Amplification':
                cnv_type = 'gain'
            elif variant['Oncomine Variant Class'] == 'Deletion':
                cnv_type = 'loss'

            params['variant_type'] = 'CNV'
            params['gene'] = variant['Genes']
            params['cnv_type'] = cnv_type

        elif variant['Type']:
            try:
                params['gene'] = variant['Genes']
                params['aa_change'] = variant['Amino Acid Change']
                params['variant_type'] = _variant_type(params['aa_change'])
            except:
                pass

        collected_params.append(params)

    # Make the POST request to PMKB
    pmkbURL = config.CONFIG_PATHS['pmkbURL']

    print ('Retrieving interpretations from PMKB... '
        'This may take a few minutes.\n'
        'PMKB URL: {}\n'.format(pmkbURL))

    responses = []
    pmkb_adapter = HTTPAdapter(max_retries=3)

    for i in collected_params:
        call = []
        call.append(i)
        url = pmkbURL
        headers = {'Content-Type': 'application/json'}

        print(call)

        session = requests.Session()
        session.mount(url,pmkb_adapter)

        try:
            response = session.post(url, data=json.dumps(call), headers=headers, verify=False, timeout=3)
            responses.append(response.json())

        except requests.ConnectionError:
            print("Failed connection to PMKB")
            print("Status Code: {}".format(response.status_code))
            print("Response: {}".format(response.text))
            print("Failed Variant:")
            print("{}\n".format(i))
            responses.append(create_dummy_json(i, "Connection Error"))
        except ValueError:
            print("No json object returned for variant:")
            print("Status Code: {}".format(response.status_code))
            print("Response: {}".format(response.text))
            print("Failed Variant:")
            print("{}\n".format(i))
            responses.append(create_dummy_json(i, "No json object"))
        except requests.Timeout:
            print("Connection timed out:")
            print("Status Code: {}".format(response.status_code))
            print("Response: {}".format(response.text))
            print("Failed Variant:")
            print("{}\n".format(i))
            responses.append(create_dummy_json(i, "Connection Timeout"))
        except:
            print("Error:")
            print("Status Code: {}".format(response.status_code))
            print("Response: {}".format(response.text))
            print("Failed Variant:")
            print("{}\n".format(i))
            responses.append(create_dummy_json(i, "Error"))

        print("\n")

    print('Interpretation lookup complete. {} variants looked up.').format(len(variants))

    # Add the relevant interpretation information into the variant dict
    interps_found = 0
    decoded_response = []
    try:
        decoded_response = responses #responses.json()
    except Exception:
        print("Error initializing responses to decoded_responses\n")
        print("responses: \n{}\n".format(responses))
        pass

    for variant, response in zip(variants, decoded_response):
        interpreted_match = None
        for match in sorted(response[0]['matches'], key=lambda d: d['relevance']):
            if match['therapies']:
                interpreted_match = match
                interps_found += 1
                break
        if interpreted_match is not None:
            interp = interpreted_match['therapies'][0]
            variant['Tier'] = interp['tier']
            variant['Interpretation'] = interp['interpretation']
            variant['Citations'] = interp['citations']

    print ('{} variants had interpretations.'.format(interps_found))

def _variant_type(aa):
    if '=' in aa:
        return 'silent'
    elif aa[-1] == "*":
      return 'nonsense'
    elif 'fs' in aa:
      return 'frameshift'
    elif 'delins' in aa:
      return 'indel'
    elif 'del' in aa:
      return 'deletion'
    elif 'ins' in aa:
      return 'insertion'
    else:
      return 'missense'

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
