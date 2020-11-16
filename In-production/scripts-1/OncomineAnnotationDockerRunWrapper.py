#!/usr/bin/env python
import argparse, os, glob, subprocess

import config
"""Calls Oncomine_Annotation_Docker (Phase 2) run with variables as specified"""

version_default='1.0.0'
SharePointBaseUrl = config.CONFIG_PATHS['SharePointBaseUrl']
#RunSheetPathDefault = InputPath+'/../../'
user_default = 'oncomine_d'
#Need to mount both the  shared bam file directory and SampleDirectory as /input
Docker_run_cmd = '''docker run --name "oncomineannotation_{SampleName}" -u {user} --rm -v {BamPath}:/input2 -v {InputPath}:/input -v {OutputPath}:/output -v {ResourcesPath}:/resources -v {RunSheetPath}:/input3 ipm-dc-dtr.weill.cornell.edu/ipm/oncorseq_phase2:{version} /bin/bash -c "bash /opt/OncorseqAnnotate.sh {SampleName} {BamName} {SharePoint} {run} 2> /output/{SampleName}.oncorseq_phase2.log"'''

#RNA only samples are samples where SampleName_RNA_v1, not SampleName_SampleName_RNA_v1
#-- just run original transform.py and push to sharepoint
Docker_run_cmd_RNA = '''docker run --name "oncomineannotation_RNAonly_{SampleName}" -u {user} --rm -v {BamPath}:/input2 -v {InputPath}:/input -v {OutputPath}:/output -v {ResourcesPath}:/resources -v {RunSheetPath}:/input3 ipm-dc-dtr.weill.cornell.edu/ipm/oncorseq_phase2:{version} /bin/bash -c "bash /resources/OncorseqAnnotate_RNAonly.sh {SampleName} {BamName} {SharePoint} {run} 2> /output/{SampleName}.oncorseq_phase2_RNA_only.log"'''

def create_directory(dir):
    dir = os.path.realpath(dir)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    return dir

def directory(arg):
    try:
        return create_directory(arg)
    except OSError:
        raise argparse.ArgumentTypeError(
            "{0} is not a valid directory".format(arg))

def main(BamPath,InputPath,OutputPath,ResourcesPath,version,user):
    rglob = glob.glob(InputPath+'/../../R*.xlsx')[0]
    #We should also copy the RUN.xlsx spreadsheets to InputPath -- These files are root/cgen-core permissions... try mounting it?
    RunSheetPath = InputPath+'/../../'
    RunName = os.path.basename(rglob).split('.')[0]
    sglob = glob.glob(InputPath+'/OCP*')[0]
    SampleName = os.path.basename(sglob).split('_v1')[0]+'_v1'
    #Also need a bam name without the _v1
    BamName = os.path.basename(sglob).split('_v1')[0]
    if '_RNA_v1' in InputPath:
        ShellRun = Docker_run_cmd_RNA.format(BamPath=BamPath,InputPath=InputPath,OutputPath=OutputPath,ResourcesPath=ResourcesPath,version=version,SampleName=SampleName,run=RunName,SharePoint=SharePointBaseUrl,user=user,BamName=BamName,RunSheetPath=RunSheetPath)
        print('Command interpretted as (RNA Only Sample): '+ShellRun)
        subprocess.call(ShellRun,shell=True)
    else:
        ShellRun = Docker_run_cmd.format(BamPath=BamPath,InputPath=InputPath,OutputPath=OutputPath,ResourcesPath=ResourcesPath,version=version,SampleName=SampleName,run=RunName,SharePoint=SharePointBaseUrl,user=user,BamName=BamName,RunSheetPath=RunSheetPath)
        print('Command interpretted as: '+ShellRun)
        subprocess.call(ShellRun,shell=True)
if __name__ == "__main__":
	parser= argparse.ArgumentParser(
	description=__doc__,
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    	parser.add_argument('BamPath',help='Full path to the shared directory of all bams for a RUN',type=directory)
	parser.add_argument('InputPath',help='Full Path to Sample Results Directory',type=directory)
	parser.add_argument('OutputPath',help='Full Path to Results Output Directory, in case you want to look at after uploading to SharePoint',type=directory)
    	parser.add_argument('ResourcesPath',help='Full Path to Resources Directory',type=directory)
        #parser.add_argument('--RunSheetPath',help='Path to where the RUN .xlsx sheet is stored.',default=InputPath+'/../../')
    	parser.add_argument('-v','--version',help='Version of Oncomine vcf to Spreadsheet Docker image to run (corresponds to image pull from respository)',default=version_default)
        parser.add_argument('-u','--user',help='What user will run the vcf to Spreadsheet pipeline',default=user_default)

	args = parser.parse_args()

main(args.BamPath,args.InputPath,args.OutputPath,args.ResourcesPath,args.version,args.user)
