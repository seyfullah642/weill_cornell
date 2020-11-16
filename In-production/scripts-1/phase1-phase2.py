#!/usr/bin/env python

import subprocess
import sys
import config
import glob
import os
from collections import defaultdict
import requests
import json

def main():

    tmpdir = config.CONFIG_PATHS['tmpdir']
    summaryLogs = config.CONFIG_PATHS['summaryLogs']
    ionreporter = config.CONFIG_PATHS['ionreporter']
    dockerDIR = config.CONFIG_PATHS['dockerBashScripts']
    p2results = config.CONFIG_PATHS['p2results']
    p1results = config.CONFIG_PATHS['p1results']
    sshkeys = config.CONFIG_PATHS['sshkeys']
    p1config = config.CONFIG_PATHS['p1config']
    p1config2 = config.CONFIG_PATHS['p1config2']
    p1imageVersion = config.CONFIG_PATHS['p1imageVersion']
    p2imageVersion = config.CONFIG_PATHS['p2imageVersion']
    p2resources = config.CONFIG_PATHS['p2resources']
    phase2wrapper = config.CONFIG_PATHS['phase2wrapper']
    p2config = config.CONFIG_PATHS['p2config']
    limsUsername = config.CONFIG_PATHS['limsUsername']
    limsPassword = config.CONFIG_PATHS['limsPassword']
    pmauth = config.CONFIG_PATHS['pmauth']
    limsapi = config.CONFIG_PATHS['limsapi']

    runs = defaultdict(list)
    countPassFail = 0

    tmpSeqInProgressFiles = glob.glob("{}/tmpSeqInProgress_*.txt".format(tmpdir))
    
    for i in tmpSeqInProgressFiles:
        f_input = open(i,"r")
        data = f_input.read().splitlines()
        for j in data:
            info = j.split("\t")
            runs[info[0]].append(info[1])
        
        f_input.close()

    for key in runs:
        f_output = open("{}/tmpAnalysisStatus_{}.txt".format(tmpdir,key),"w")
        for i in runs[key]:
            comprehensive = subprocess.call(["ssh", ionreporter, "test -e", "/data/IR/data/IR_Org/ion.reporter@lifetech.com/{}_v1_{}_RNA_v1/{}*/summary.log".format(i,i,i)])
            dna_only = subprocess.call(["ssh", ionreporter, "test -e", "/data/IR/data/IR_Org/ion.reporter@lifetech.com/{}_v1/{}*/summary.log".format(i,i)])
            rna_only = subprocess.call(["ssh", ionreporter, "test -e", "/data/IR/data/IR_Org/ion.reporter@lifetech.com/{}_RNA_v1/{}*/summary.log".format(i,i)])

            if comprehensive == 0:
                ssh = subprocess.Popen(["ssh", ionreporter, "cat", "/data/IR/data/IR_Org/ion.reporter@lifetech.com/{}_v1_{}_RNA_v1/{}*/summary.log".format(i,i,i)] \
                                           ,stdout=subprocess.PIPE)
                python = subprocess.Popen([summaryLogs],stdin=ssh.stdout, stdout=subprocess.PIPE,shell=True)
                ssh.stdout.close()
                output = python.communicate()
                f_output.write("{}\t{}\t{}\n".format(i,output[0].rstrip(),key))

            elif dna_only == 0:
                ssh = subprocess.Popen(["ssh", ionreporter, "cat", "/data/IR/data/IR_Org/ion.reporter@lifetech.com/{}_v1/{}*/summary.log".format(i,i)] \
                                           ,stdout=subprocess.PIPE)
                python = subprocess.Popen([summaryLogs],stdin=ssh.stdout, stdout=subprocess.PIPE,shell=True)
                ssh.stdout.close()
                output = python.communicate()
                f_output.write("{}\t{}\t{}\n".format(i,output[0].rstrip(),key))

            elif rna_only == 0:
                ssh = subprocess.Popen(["ssh", ionreporter, "cat", "/data/IR/data/IR_Org/ion.reporter@lifetech.com/{}_RNA_v1/{}*/summary.log".format(i,i)] \
                                           ,stdout=subprocess.PIPE)
                python = subprocess.Popen([summaryLogs],stdin=ssh.stdout, stdout=subprocess.PIPE,shell=True)
                ssh.stdout.close()
                output = python.communicate()
                f_output.write("{}\t{}\t{}\n".format(i,output[0].rstrip(),key))

            else:
                f_output.write("{}\tFile doesn't exist\t{}\n".format(i,key))
                    
        f_output.close()

    tmpAnalysisStatusFiles = glob.glob("{}/tmpAnalysisStatus_*.txt".format(tmpdir))
    
    for files in tmpAnalysisStatusFiles:
        filename = os.path.basename(files)
        filename = filename.split("_")
        runNum = filename[1].split(".")
        runNum = runNum[0]
        numOFsamps = len(runs[runNum])

        f_input = open(files,"r")
        data = f_input.read().splitlines()

        for lines in data:
            line = lines.split("\t")
            if line[1] == "Analysis complete" or line[1] == "Analysis failed":
                countPassFail = countPassFail + 1

        if os.stat(files).st_size != 0 and countPassFail == numOFsamps:
            f_output = open("{}/docker_phase1_phase2_RUN{}.sh".format(dockerDIR,runNum),"w")
            #Phase 1 docker command
            f_output.write("#!/bin/bash\n\n")
            f_output.write("docker run -i -e RUNID=RUN{} --rm -v {}:/phase01/OnCORSeq_phase2_results/ -v {}:/phase01/OnCORSeq_phase1_results/ -v {}:/phase01/logs/ -v {}:/root/.ssh -v {}:/phase01/scripts/config.cfg -v {}:/phase01/scripts/config.py {}\nwait\n\n".format(runNum,p2results,p1results,p2results,sshkeys,p1config,p1config2,p1imageVersion))
            #Phase 2 docker command
            f_output.write("samples=( $(find {}/RUN{}/OCP*/OCP* -maxdepth 0 -name 'OCP*' -type d) )\n\n".format(p2results,runNum))
            f_output.write("for i in ${samples[@]};do\n")
            f_output.write("\t{} RUN{} {}/RUN{}/bam $i {}/RUN{}/spreadsheets {} {} -v {}\n".format(phase2wrapper,runNum,p1results,runNum,p2results,runNum,p2resources,p2config,p2imageVersion))
            f_output.write("done")
            
            f_output.close()
            os.chmod("{}/docker_phase1_phase2_RUN{}.sh".format(dockerDIR,runNum), 0o777)
            
            filename = os.path.basename(files)

            auth_url = pmauth
            token_headers = {'content-type':'application/json'}
            token_body = {'username':'{}'.format(limsUsername),'password':'{}'.format(limsPassword)}

            token_req = requests.post(auth_url, headers=token_headers, data=json.dumps(token_body))
            token = token_req.json()

            print("Token request status code:")
            print(token_req.status_code)

            for records in data:
                print(records)
                line = records.split("\t")
                sample_url = "{}/{}".format(limsapi, line[0])
                sample_headers = {'accept':'application/json', 'Authorization':'{}'.format(token['Token'])}

                if line[1] == "Analysis complete":
                    sample_body = {'status':'ANNOTATION IN PROGRESS'}
                    print(sample_body)
                    sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))
                    print(sample_req.status_code)

                elif line[1] == "Analysis failed":
                    sample_body = {'status':'FAILED ANALYSIS'}
                    print(sample_body)
                    sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))
                    print(sample_req.status_code)

                else:
                    sample_body = {'status':'FAILED - OTHER'}
                    print(sample_body)
                    sample_req = requests.put(sample_url, headers=sample_headers, data=json.dumps(sample_body))
                    print(sample_req.status_code)
   
if __name__ == '__main__':
  main()

