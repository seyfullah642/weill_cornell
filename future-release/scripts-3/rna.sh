#!/bin/bash

# run=$1
# sampleID=$2

log() {

PROGRAM=`basename "${0}"`
STATUS=${1}
MESSAGE=${2}
printf "[ $(date '+%b %d %R:%S') ] ${PROGRAM}:\t${STATUS}\t${MESSAGE}\n\n" >> /OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}.oncorseq_phase2.log
}

run=!{run}
sampleID=!{sampleID}
vcf=!{vcf}

printf '${vcf}\n'

source /opt/config.cfg

FILE=/OnCORSeq_phase2_results/${run}/spreadsheets/${sampleID}.oncorseq_phase2.log
if [ -f "${FILE}" ]; then
    rm ${FILE}
fi

log "INFO" " ${run}, ${sampleID}, ${dnaBarcode}, ${rnaBarcode}"

# ${updateLIMS} ${sampleID}

log "INFO" " Transfering vcf file into opt dir"
rsync -av /OnCORSeq_phase2_results/${run}/${sampleID}_RNA_v1*/${sampleID}_RNA_v1*/outputs/AnnotatorActor-00/${sampleID}*_v1*.vcf /opt/
if [ "$?" -eq "0" ]; then
    log "INFO" " Transfer SUCCESSFUL"
else
    log "ERROR" " Transfer UNSUCCESSFUL"
    exit 1
fi

log "INFO" " Renaming vcf file"
mv /opt/${sampleID}*_v1*.vcf /opt/${sampleID}_v1.vcf

log "INFO" " cd into opt"
cd /opt

log "INFO" " Running transform.py"
python transform.py /opt /opt/${sampleID}.xls
if [ "$?" -eq "0" ]; then
    log "INFO" " transform_v2.py SUCCESSFUL"
else
    log "ERROR" " transform_v2.py UNSUCCESSFUL"
    exit 1
fi

log "INFO" " Running Dockerized_HyperLinks_RNAonly.py"
python Dockerized_HyperLinks_RNAonly.py /opt/${sampleID}.xls ${run}
if [ "$?" -eq "0" ]; then
    log "INFO" " Dockerized_HyperLinksRNAonly.py SUCCESSFUL"
else
    log "ERROR" " Dockerized_HyperLinksRNAonly.py UNSUCCESSFUL"
    exit 1
fi

log "INFO" " Running uploadtoSharepoint.py"
python uploadtoSharepoint.py ${SharePoint}/${run}/${sampleID}/Generated_Report/ ${sampleID}_final.xlsx
if [ "$?" -eq "0" ]; then
    log "INFO" " uploadtoSharepoint.py SUCCESSFUL"
else
    log "ERROR" " uploadtoSharepoint.py UNSUCCESSFUL"
    exit 1
fi

log "INFO" " Transferring ${sampleID}_final.xlsx to spreadsheets dir"
rsync -av /opt/${sampleID}_final.xlsx /OnCORSeq_phase2_results/${run}/spreadsheets/
if [ "$?" -eq "0" ]; then
    log "INFO" " Transfer SUCCESSFUL"
else
    log "ERROR" " Transfer UNSUCCESSFUL"
    exit 1
fi