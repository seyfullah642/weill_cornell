from requests.adapters import HTTPAdapter
import requests
import config
import json


def get_record_info_limsapi(sampleName):
    print('Pulling data from lims for {}...'.format(sampleName))

    limsUsername = config.CONFIG_PATHS['limsUsername']
    limsPassword = config.CONFIG_PATHS['limsPassword']
    pmauth = config.CONFIG_PATHS['pmauth']
    limsapi = config.CONFIG_PATHS['limsapi']

    auth_url = pmauth
    token_headers = {'content-type': 'application/json'}
    token_body = {'username': '{}'.format(limsUsername), 'password': '{}'.format(limsPassword)}

    token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
    token = token_req.json()

    print("Token request status code:")
    print(token_req.status_code)

    # Get entire oncorseq spreadsheet or by just sample GET IS TO GET AN ENTRY
    sample_url = "{}/{}".format(limsapi, sampleName)
    sample_headers = {'accept': 'application/json', 'Authorization': '{}'.format(token['Token'])}
    sample_req = requests.get(sample_url, headers=sample_headers)
    sample_record = sample_req.json()

    return sample_record['dataRecords'][0]['fields']


def get_interpretations(variants, sample_fields):
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
        session.mount(url, pmkb_adapter)

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
    except:
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

    print('{} variants had interpretations.'.format(interps_found))


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


def create_dummy_json(variant=None, error=None):
    response = []
    call = {}
    match = [{'relevance': 1, 'variants': 'NA',
              'therapies': [{'interpretation': '{}'.format(error), 'citations': [{'citation': '{}'.format(error)}],
                             'tier': '{}'.format(error)}]
              }]

    call['params'] = variant
    call['status'] = "1 matches"
    call['matches'] = match
    response.append(call)

    return response


if __name__ == '__main__':
    create_dummy_json()
