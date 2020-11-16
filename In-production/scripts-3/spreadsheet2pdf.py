#!/usr/bin/env python2.7

import subprocess
import os
import config
import json
import requests
from datetime import datetime

def main():

    usrPass = config.CONFIG_PATHS['usrPass']
    baseURL = config.CONFIG_PATHS['SharePointBaseUrl']
    downloadFromSharePoint = config.CONFIG_PATHS['downloadFromSharePoint']
    uploadToSharePoint = config.CONFIG_PATHS['uploadToSharePoint']
    reportGen = config.CONFIG_PATHS['report']
    failedreportGen = config.CONFIG_PATHS['failedReport']
    reportdir = config.CONFIG_PATHS['reportdir']
    uploadToSharePoint = config.CONFIG_PATHS['uploadToSharePoint']
    limsUsername = config.CONFIG_PATHS['limsUsername']
    limsPassword = config.CONFIG_PATHS['limsPassword']
    pmauth = config.CONFIG_PATHS['pmauth']
    limsapi = config.CONFIG_PATHS['limsapi']

    date = datetime.today().strftime('%b %d, %Y')

    #Post for token
    auth_url = pmauth
    token_headers = {'content-type':'application/json'}
    token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

    token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
    token = token_req.json()

    print("Token request status code:")
    print(token_req.status_code)

    #Get entire oncorseq spreadsheet or by just sample GET IS TO GET AN ENTRY
    lims_url = limsapi
    lims_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
    lims_req = requests.get(lims_url, headers=lims_headers)
    lims_records = lims_req.json() 

    for key in lims_records['dataRecords']:
        if key['fields']['Status'] == "READY FOR REPORT GENERATION" or key['fields']['Status'] == "GENERATE FAILED REPORT":
            print(key['fields'])

    for key in lims_records['dataRecords']:

        if key['fields']['Status'] == "READY FOR REPORT GENERATION":

            print("\n")
            print(key['fields']['SampleId'])
            print(key['fields']['Status'])
            print(key['fields'])

            url1 = "{}/RUN{}/{}/Generated_Report/Final_Report/{}_reviewed.xlsx".format(baseURL, key['fields']['SequencingRunId'], key['fields']['SampleId'], key['fields']['SampleId'])
            print(url1)
            url2 = "{}/RUN{}/{}/Generated_Report/Final_Report/{}.pdf".format(baseURL, key['fields']['SequencingRunId'], key['fields']['SampleId'], key['fields']['SampleId'])
            print(url2)

            reviewed_sheet = subprocess.call(["curl", "--ntlm", "-u", usrPass, "--output", "/dev/null", "--silent", "--head", "--fail",url1,"-k"])
            pdf_report = subprocess.call(["curl", "--ntlm", "-u", usrPass, "--output", "/dev/null", "--silent", "--head", "--fail",url2,"-k"])

            print(reviewed_sheet)
            print(pdf_report)
    
            if reviewed_sheet != 0:
                sample_url = "{}/{}".format(limsapi, key['fields']['SampleId'])
                sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
                sample_body = {'status':'ERROR - REVIEWED SPREADSHEET DOES NOT EXIST'}
                sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))

            if reviewed_sheet == 0 and pdf_report != 0:
                subprocess.call([downloadFromSharePoint,"{}/RUN{}/{}/Generated_Report/Final_Report/{}_reviewed.xlsx".format(baseURL, key['fields']['SequencingRunId'], key['fields']['SampleId'], key['fields']['SampleId']), \
                "{}_reviewed.xlsx".format(key['fields']['SampleId'])]) 

                subprocess.call([reportGen, "{}_reviewed.xlsx".format(key['fields']['SampleId']), "{}/".format(reportdir)])

                if os.path.isfile("{}/{}.pdf".format(reportdir, key['fields']['SampleId'])):
                    subprocess.call([uploadToSharePoint, "{}/RUN{}/{}/Generated_Report/Final_Report/".format(baseURL, key['fields']['SequencingRunId'], key['fields']['SampleId']), \
                                    "{}/{}.pdf".format(reportdir, key['fields']['SampleId'])])

                    sample_url = "{}/{}".format(limsapi, key['fields']['SampleId'])
                    sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
                    sample_body = {'status':'READY FOR SIGN OUT', 'date_report_generation':'{}'.format(date)}
                    sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))

                else:
                    sample_url = "{}/{}".format(limsapi, key['fields']['SampleId'])
                    sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
                    sample_body = {'status':'ERROR - REVIEWED SPREADSHEET MALFORMED'}
                    sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))

            if  reviewed_sheet == 0 and pdf_report == 0:
                sample_url = "{}/{}".format(limsapi, key['fields']['SampleId'])
                sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
                sample_body = {'status':'WARNING - REPORT ALREADY EXISTS'}
                sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))

        if key['fields']['Status'] == "GENERATE FAILED REPORT":

            subprocess.call([failedreportGen, "{}".format(key['fields']['SampleId']), "{}/".format(reportdir)])
            subprocess.call([uploadToSharePoint, "{}/Failed_Reports/".format(baseURL), "{}/{}.pdf".format(reportdir, key['fields']['SampleId'])])

            sample_url = "{}/{}".format(limsapi, key['fields']['SampleId'])
            sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
            sample_body = {'status':'FAILED REPORT READY FOR SIGN OUT'}
            sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))

if __name__ == '__main__':
  main()
