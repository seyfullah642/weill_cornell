#!/usr/bin/env python

import subprocess
from subprocess import Popen, PIPE
import sys
import os
import config
import glob
import requests
import json

def main():

    usrPass = config.CONFIG_PATHS['usrPass']
    baseURL = config.CONFIG_PATHS['SharePointBaseUrl']
    tmpdir = config.CONFIG_PATHS['tmpdir']
    limsUsername = config.CONFIG_PATHS['limsUsername']
    limsPassword = config.CONFIG_PATHS['limsPassword']
    pmauth = config.CONFIG_PATHS['pmauth']
    limsapi = config.CONFIG_PATHS['limsapi']

    tmpAnnInProgressFiles = glob.glob("{}/tmpAnnInProgress_*.txt".format(tmpdir))
    
    for i in tmpAnnInProgressFiles:
        
        f_input = open(i,"r")
        data = f_input.read().splitlines()

        for i in data:
            info = i.split("\t")
            url = "{}/RUN{}/{}/Generated_Report/{}_v1_final.xlsx".format(baseURL,info[0],info[1],info[1])
            test = subprocess.call(["curl", "--ntlm", "-u", usrPass, "--output", "/dev/null", "--silent", "--head", "--fail",url,"-k"])

            if test == 0:
                auth_url = pmauth
                token_headers = {'content-type':'application/json'}
                token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

                token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
                token = token_req.json()

                print("Token request status code:")
                print(token_req.status_code)

                sample_url = "{}/{}".format(limsapi, info[1])
                sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}
                sample_body = {'status':'READY FOR REVIEW'}
                print(sample_body)

                sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))
                print(sample_req.status_code)

if __name__ == '__main__':
  main()
