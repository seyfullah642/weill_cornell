#!/bin/bash

# run=$1
# sampleID=$2
# dnaBarcode=$3
# rnaBarcode=$4

log() {

    PROGRAM=`basename "${0}"`
    STATUS=${1}
    MESSAGE=${2}
    printf "[ $(date '+%b %d %R:%S') ] ${PROGRAM}:\t${STATUS}\t${MESSAGE}\n\n" >> /OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}.oncorseq_phase2.log
}

run=!{run}
sampleID=!{sampleID}
resourceDir=!{resourceDir}
bam=!{bam}
vcf=!{vcf}

printf "${vcf}\n\n"
printf "${bam}\n\n"

# working_dir=`pwd`

# source /opt/config.cfg

# FILE=/OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}.oncorseq_phase2.log

# if [ -f "${FILE}" ]; then
#     rm ${FILE}
# fi

# log "INFO" " ${run}, ${sampleID}, ${dnaBarcode}, ${rnaBarcode}"

# # ${updateLIMS} ${sampleID}

# log "INFO" " Exporting samtool dir"
# export samtools_dir
# log "INFO" " Exporting bcftools dir"
# export bcftools_dir

# log "INFO" " Transfering vcf file into opt dir"
# rsync -av /OnCORSeq_phase2_results/${run}/${sampleID}_v1*/${sampleID}_v1*/outputs/AnnotatorActor-00/${sampleID}*_v1*.vcf /opt/
# if [ "$?" -eq "0" ]; then
#     log "INFO" " Transfer SUCCESSFUL"
# else
#     log "ERROR" " Transfer UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Renaming vcf file"
# mv /opt/${sampleID}*_v1*.vcf /opt/${sampleID}_v1.vcf

# log "INFO" " cd into opt"
# cd /opt

# log "INFO" " Running dockerized_annotate_vcf.sh"
# bash dockerized_annotate_vcf.sh /opt/${sampleID}_v1.vcf ${working_dir}/${resourceDir}
# if [ "$?" -eq "0" ]; then
#     log "INFO" " dockerized_annotate_vcf.sh SUCCESSFUL"
# else
#     log "ERROR" " dockerized_annotate_vcf.sh UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Running Dockerized_mpileup.v2.py"
# python Dockerized_mpileup.v2.py /OnCORSeq_phase1_results/${run}/bam/${sampleID}_rawlib.bam --reference ${working_dir}/${resourceDir}/hg19.chr.fa --regions ${working_dir}/${resourceDir}/Wei_pert_neg_amplicons.bed \
#                                 --PertNegSheet ${working_dir}/${resourceDir}/2017_05_25.pertinent_negative_list.EXaCT-1.csv --shell_dir /opt/
# if [ "$?" -eq "0" ]; then
#     log "INFO" " Dockerized_mpileup.v2.py SUCCESSFUL"
# else
#     log "ERROR" " Dockerized_mpileup.v2.py UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Running mpileup_Oncomine*.sh"
# bash -x /opt/mpileup_Oncomine*.sh
# if [ "$?" -eq "0" ]; then
#     log "INFO" " mpileup_Oncomine*.sh SUCCESSFUL"
# else
#     log "ERROR" " mpileup_Oncomine*.sh UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Running Dockerized_transform_v2.py"
# python Dockerized_transform_v2.py /opt /opt/${sampleID}.xls
# if [ "$?" -eq "0" ]; then
#     log "INFO" " Dockerized_transform_v2.py SUCCESSFUL"
# else
#     log "ERROR" " Dockerized_transform_v2.py UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Transferring ${sampleID}.xls.extendedAnn.xls to spreadsheets dir"
# rsync -av /opt/${sampleID}.xls.extendedAnn.xls /OnCORSeq_phase2_results/${run}/spreadsheets/
# if [ "$?" -eq "0" ]; then
#     log "INFO" " Transfer SUCCESSFUL"
# else
#     log "ERROR" " Transfer UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Running Dockerized_HyperLinks.py"
# python Dockerized_HyperLinks.py /OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}.xls.extendedAnn.xls ${run} ${working_dir}/${resourceDir}/Ensembl.human_v75_b37.gene_table.txt
# if [ "$?" -eq "0" ]; then
#     log "INFO" " Dockerized_HyperLinks.py SUCCESSFUL"
# else
#     log "ERROR" " Dockerized_HyperLinks.py UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Running uploadtoSharepoint.py"
# python uploadtoSharepoint.py ${SharePoint}/${run}/${sampleID}/Generated_Report/ /OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}_final.xlsx
# if [ "$?" -eq "0" ]; then
#     log "INFO" " uploadtoSharepoint.py SUCCESSFUL"
# else
#     log "ERROR" " uploadtoSharepoint.py UNSUCCESSFUL"
#     exit 1
# fi

# log "INFO" " Removing ${sampleID}.xls.extendedAnn.xls"
# rm /OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}.xls.extendedAnn.xls