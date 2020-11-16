#!/usr/bin/env python

"""Samtools mpileup on Oncomine data, pertinent negative regions only to ensure absence of any variants here."""
import argparse
import subprocess
import sys
import os
import re
import datetime
from getpass import getuser
user = getuser()
startTime = datetime.datetime.now()
#This needs to be changed depending on environment
reference_genome_default='/resources/hg19.chr.fa' #Change the path
output_base_directory_default=os.getcwd()+'/'
samtools_location='$samtools_dir/samtools' #Change the path
bcftools_location='$bcftools_dir/bcftools' #Change the path
shell_dir_default=os.getcwd()+'/'
#This needs to be changed depending on environment
regions_default = '/resources/Wei_pert_neg_amplicons.bed ' #The pertinent negatives bedfile -- need this within Docker! -- change path
PertNegSheet_default= '/resources/2017_05_25.pertinent_negative_list.EXaCT-1.csv' #PertinentNegatives csv file, needed within Docker
#Runs fast enough without qsub
samtools_cmd = "{samtools} mpileup -ugD -A -d 4000 -f {reference} -l {regions} {TUMOR} | {bcftools} call -mA -o {output_dir}/{output}.mpileup.vcf "
#We also want to include the parsing via Rscript
parse_cmd = "Rscript /opt/parse_Oncomine_pertneg_v2.R {output_dir}/{output}.mpileup.vcf {PertNegSheet}" ##Change the .R file path
#samtools_cmd = "{samtools} mpileup -A -d 4000 -f {reference} -l {regions} {TUMOR} | awk '{{print $1,$2,$3,$4}}' > {output_dir}/{output}.mpileup "

def file_exists(arg):
    if os.path.isfile(arg):
        return os.path.realpath(arg)
    else:
        raise argparse.ArgumentTypeError("{0} is not a valid file".format(arg))

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

def main(reference,tumor_bam,shell_dir,output_dir,regions,PertNegSheet):
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)
	output = tumor_bam.split('/')[-1]
	with open("{shell_dir}/mpileup_Oncomine_{output}.sh".format(shell_dir=shell_dir,output=output),'w+') as shell:
		shell.write(samtools_cmd.format(samtools=samtools_location,bcftools=bcftools_location,reference=reference,
                                        regions=regions,TUMOR=tumor_bam,
                                        output_dir=output_dir,output=output)+'\n')
        	shell.write(parse_cmd.format(output_dir=output_dir,output=output,PertNegSheet=PertNegSheet))

if __name__ == "__main__":
	parser= argparse.ArgumentParser(
	description=__doc__,
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-r','--reference',help="Reference genome",default=reference_genome_default)
	parser.add_argument('TUMOR',help='Affected tissue bam',type= file_exists)
	parser.add_argument('-s','--shell_dir',type=directory,help='Directory to output shells',default=shell_dir_default)
	parser.add_argument('--output_dir',help='Where to output the variant calls', type=directory,default=output_base_directory_default)
	parser.add_argument('--regions',help='The bed file of pertinent negatives',default=regions_default)
    	parser.add_argument('--PertNegSheet',help='The .csv of pertinent negative targets',default=PertNegSheet_default)
	args = parser.parse_args()

main(args.reference,args.TUMOR,args.shell_dir,args.output_dir,args.regions,args.PertNegSheet)
