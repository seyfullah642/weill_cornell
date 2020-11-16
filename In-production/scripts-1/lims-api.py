#!/usr/bin/env python

import config
from collections import defaultdict
import requests
import json

def main():

    limsUsername = config.CONFIG_PATHS['limsUsername']
    limsPassword = config.CONFIG_PATHS['limsPassword']
    tmpdir = config.CONFIG_PATHS['tmpdir']
    pmauth = config.CONFIG_PATHS['pmauth']
    limsapi = config.CONFIG_PATHS['limsapi']

    auth_url = pmauth
    token_headers = {'content-type':'application/json'}
    token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

    token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
    token = token_req.json()

    print("Token request status code:")
    print(token_req.status_code)
    
    lims_url = limsapi
    lims_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
    lims_req = requests.get(lims_url, headers=lims_headers)
    lims_records = lims_req.json() 

    runs_seq = defaultdict(list)
    #print(lims_records, "\n")
    for key in lims_records['dataRecords']:
        if key['fields']['Status'] == "SEQUENCING IN PROGRESS":
            runs_seq[key['fields']['SequencingRunId']].append(key['fields']['SampleId'])

    if bool(runs_seq):
        #f_output_seq = open("{}/tmpSeqInProgress_{}.txt".format(tmpdir,key),"w")
        for key in runs_seq:
            f_output_seq = open("{}/tmpSeqInProgress_{}.txt".format(tmpdir,key),"w")
            for i in runs_seq[key]:
                f_output_seq.write("{}\t{}\n".format(key,i))

        f_output_seq.close()

    runs_ann = defaultdict(list)   

    for key in lims_records['dataRecords']:
        if key['fields']['Status'] == "ANNOTATION IN PROGRESS":
            runs_ann[key['fields']['SequencingRunId']].append(key['fields']['SampleId'])

    #print(runs_ann)
    if bool(runs_ann):
        for key in runs_ann:
            f_output_ann = open("{}/tmpAnnInProgress_{}.txt".format(tmpdir,key),"w")
            for i in runs_ann[key]:
                f_output_ann.write("{}\t{}\n".format(key,i))

        f_output_ann.close()

if __name__ == '__main__':
  main()
