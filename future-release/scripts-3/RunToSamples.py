#!/usr/bin/env python3

import requests
import json
import importlib.util
import subprocess
#import config
import re

spec = importlib.util.spec_from_file_location("config", "/config/RunToSamples/config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

limsUsername = config.CONFIG_PATHS['limsUsername']
limsPassword = config.CONFIG_PATHS['limsPassword']
pmauth = config.CONFIG_PATHS['pmauth']
limsapi = config.CONFIG_PATHS['limsapi']
ionreporter = config.CONFIG_PATHS['ionreporter']

def main():

    auth_url = pmauth
    token_headers = {'content-type':'application/json'}
    token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

    token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
    token = token_req.json()

    print(f"Token request status code: {token_req.status_code}\n")
    
    lims_url = limsapi
    lims_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
    lims_req = requests.get(lims_url, headers=lims_headers)
    lims_records = lims_req.json() 

    mapping = open("mapping.csv","w")

    mapping.write("run,sampleID,DNABarcode,RNABarcode,chipNum\n")

    for key in lims_records['dataRecords']:
        if key['fields']['Status'] == "SEQUENCING IN PROGRESS":

            print(f"{key['fields']['SampleId']}")
            run_test_command(key['fields']['SampleId'])
            analysis_status = run_test_command(key['fields']['SampleId'])
            print(f'{analysis_status}')

            if analysis_status == "Analysis Complete":
                    create_mapping_csv(mapping,key['fields']['LibraryBatchId'], key['fields']['SampleId'], key['fields']['DNABarcode'], key['fields']['RNABarcode'],key['fields']['SequencingChipId'])

    mapping.close()

def create_mapping_csv(csv,runNum,sampleID,dnaBarcode,rnaBarcode,chipNum):

    csv.write(f"{runNum},{sampleID},{dnaBarcode},{rnaBarcode},{chipNum}\n")

def run_test_command(sampleID):

    comprehensive = subprocess.call(["ssh", ionreporter, "test -e", f"/data/IR/data/IR_Org/ion.reporter@lifetech.com/{sampleID}_v1_{sampleID}_RNA_v1/{sampleID}*/summary.log"])
    dna_only = subprocess.call(["ssh", ionreporter, "test -e", f"/data/IR/data/IR_Org/ion.reporter@lifetech.com/{sampleID}_v1/{sampleID}*/summary.log"])
    rna_only = subprocess.call(["ssh", ionreporter, "test -e", f"/data/IR/data/IR_Org/ion.reporter@lifetech.com/{sampleID}_RNA_v1/{sampleID}*/summary.log"])

    if comprehensive == 0:
        ssh = subprocess.Popen(["ssh", ionreporter, "cat", f"/data/IR/data/IR_Org/ion.reporter@lifetech.com/{sampleID}_v1_{sampleID}_RNA_v1/{sampleID}*/summary.log"], stdout=subprocess.PIPE)
        while True:

            output = ssh.stdout.read()
            line = output.rstrip().decode('utf-8')

            if re.search(r'TsPluginActor finished.',line) or re.search(r'TsPluginActor/runPlugin succeeded.',line) \
            or re.search(r'AppRunnerActor finished.',line) or re.search(r'QcmoduleActor finished',line):
                return "Analysis Complete"

            elif re.search(r'TsPluginActor cancelled because dependency failed.',line) or \
                re.search(r'AnnotatorActor cancelled because dependency failed.',line):
                return "Analysis Failed"

            else:
                return "Analysis not yet complete"

    if dna_only == 0:
        ssh = subprocess.Popen(["ssh", ionreporter, "cat", f"/data/IR/data/IR_Org/ion.reporter@lifetech.com/{sampleID}_v1/{sampleID}*/summary.log"], stdout=subprocess.PIPE)
        while True:

            output = ssh.stdout.read()
            line = output.rstrip().decode('utf-8')

            if re.search(r'TsPluginActor finished.',line) or re.search(r'TsPluginActor/runPlugin succeeded.',line) \
            or re.search(r'AppRunnerActor finished.',line) or re.search(r'QcmoduleActor finished',line):
                return "Analysis Complete"

            elif re.search(r'TsPluginActor cancelled because dependency failed.',line) or \
                re.search(r'AnnotatorActor cancelled because dependency failed.',line):
                return "Analysis Failed"

            else:
                return "Analysis not yet complete"

    if rna_only == 0:
        ssh = subprocess.Popen(["ssh", ionreporter, "cat", f"/data/IR/data/IR_Org/ion.reporter@lifetech.com/{sampleID}_RNA_v1/{sampleID}*/summary.log"], stdout=subprocess.PIPE)
        while True:

            output = ssh.stdout.read()
            line = output.rstrip().decode('utf-8')

            if re.search(r'TsPluginActor finished.',line) or re.search(r'TsPluginActor/runPlugin succeeded.',line) \
            or re.search(r'AppRunnerActor finished.',line) or re.search(r'QcmoduleActor finished',line):
                return "Analysis Complete"

            elif re.search(r'TsPluginActor cancelled because dependency failed.',line) or \
                re.search(r'AnnotatorActor cancelled because dependency failed.',line):
                return "Analysis Failed"

            else:
                return "Analysis not yet complete"


if __name__ == '__main__':
  main()
