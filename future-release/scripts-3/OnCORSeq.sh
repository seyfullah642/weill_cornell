#!/usr/bin/env bash

log() {

    PROGRAM=`basename "${0}"`
    STATUS=${1}
    MESSAGE=${2}
    printf "[ $(date '+%b %d %R:%S') ] ${PROGRAM}:\t${STATUS}\t${MESSAGE}\n\n" >> ${logs}/${run}/${sampleID}.log
}

run=!{run}
sampleID=!{sampleID}
dnaBarcode=!{DNAbarcode}
rnaBarcode=!{RNABarcode}
chipNum=!{chipNum}
resultsBAMDir=bam
resultsVCFDir=vcf


source /phase01/scripts/config.cfg
#exec > ${logs}/${run}/${sampleID}.log 2>&1

FILE=${logs}/${run}/${sampleID}.log
if [ -f "${FILE}" ]; then
    rm ${FILE}
fi

log "INFO" " ${run}, ${sampleID}, ${dnaBarcode}, ${rnaBarcode}, ${chipNum}"

# log "INFO" " Updating lims for ${sampleID}"
# ${updateLIMS} ${sampleID}

log "INFO" " Creating a ${run} directory"
mkdir ${outputFILES}/${run}
mkdir ${outputBAM}/${run}
mkdir ${outputBAM}/${run}/bam
mkdir ${outputFILES}/${run}/spreadsheets
mkdir ${resultsBAMDir}
mkdir ${resultsVCFDir}


log "INFO" " Transfer of analysis folder for ${sampleID} has initialized"

analysis=1
while [ ${analysis} -lt 4 ]; do
    let analysis=analysis+1
    log "INFO" " Transfer attempt of analysis folder ${sampleID}: ${analysis}"
    rsync -av ${IonReporter}/${sampleID}_* ${resultsVCFDir}/

    if [ "$?" -eq "0" ]; then
        log "INFO" " Analysis folder for ${sampleID} has transferred SUCCESSFUL"
        break
    else
        log "ERROR" " Analysis folder for ${sampleID} has transferred UNSUCCESSFUL"
        exit 1
    fi
done

log "INFO" " ${dnaBarcode}_rawlib.bam file transfer initialized"
if [ "${dnaBarcode}" != "NA" ]; then

    dna_bam=1
    while [ ${dna_bam} -lt 4 ]; do
        let dna_bam=dna_bam+1
        log "INFO" " Transfer attempt for ${dnaBarcode}_rawlib.bam: ${dna_bam}"
        # TODO rsync -av ${TorrentServer}/Auto_user_S5XL-*-*-OCP_${run}_CHIP${chipNum}_[0-9][0-9][0-9]_[0-9][0-9][0-9]/${dnaBarcode}_rawlib.bam ${outputBAM}/${run}/bam
        rsync -av ${TorrentServer}/Auto_user_S5XL-*-*-OCP_${run}_CHIP${chipNum}_[0-9][0-9][0-9]_[0-9][0-9][0-9]/${dnaBarcode}_rawlib.bam ${resultsBAMDir}/
        if [ "$?" -eq "0" ]; then
            log "INFO" " ${dnaBarcode}_rawlib.bam file transfer SUCCESSFUL"
            break
        else
            log "ERROR" " ${dnaBarcode}_rawlib.bam file transfer UNSUCCESSFUL"
            exit 1
        fi
    done

    dna_bai=1
    while [ ${dna_bai} -lt 4 ]; do
        let dna_bai=dna_bai+1
        log "INFO" " Transfer attempt for ${dnaBarcode}_rawlib.bam.bai: ${dna_bai}"
        # TODO rsync -av ${TorrentServer}/Auto_user_S5XL-*-*-OCP_${run}_CHIP${chipNum}_[0-9][0-9][0-9]_[0-9][0-9][0-9]/${dnaBarcode}_rawlib.bam.bai ${outputBAM}/${run}/bam
        rsync -av ${TorrentServer}/Auto_user_S5XL-*-*-OCP_${run}_CHIP${chipNum}_[0-9][0-9][0-9]_[0-9][0-9][0-9]/${dnaBarcode}_rawlib.bam.bai ${resultsBAMDir}/
        if [ "$?" -eq "0" ]; then
            log "INFO" " ${dnaBarcode}_rawlib.bam.bai file transfer SUCCESSFUL"
            break
        else
            log "ERROR" " ${dnaBarcode}_rawlib.bam.bai file transfer UNSUCCESSFUL"
            exit 1
        fi
    done

    log "INFO" " Renaming ${sampleID} bam files from BarcodeID to SampleID"
    mv ${resultsBAMDir}/${dnaBarcode}_rawlib.bam ${resultsBAMDir}/${sampleID}_rawlib.bam
    mv ${resultsBAMDir}/${dnaBarcode}_rawlib.bam.bai ${resultsBAMDir}/${sampleID}_rawlib.bam.bai

else
    log "INFO" " No DNA bam file for ${sampleID}"
fi

log "INFO" " ${rnaBarcode}_rawlib.basecaller.bam file transfer initialized"
if [ "${rnaBarcode}" != "NA" ]; then

    rna_bam=1
    while [ ${rna_bam} -lt 4 ]; do
        let rna_bam=rna_bam+1
        log "INFO" " Transfer attempt for ${rnaBarcode}_rawlib.basecaller.bam: ${rna_bai}"
        rsync -av ${TorrentServer}/Auto_user_S5XL-*-*-OCP_${run}_CHIP${chipNum}_[0-9][0-9][0-9]_[0-9][0-9][0-9]/basecaller_results/${rnaBarcode}_rawlib.basecaller.bam ${outputBAM}/${run}/bam

        if [ "$?" -eq "0" ]; then
            log "INFO" " ${rnaBarcode}_rawlib.basecaller.bam file transfer SUCCESSFUL"
            break
        else
            log "ERROR" " ${rnaBarcode}_rawlib.basecaller.bam file transfer UNSUCCESSFUL"
            exit 1
        fi
    done

    log "INFO" " Renaming ${sampleID} bam files from BarcodeID to SampleID"
    mv ${outputBAM}/${run}/bam/${rnaBarcode}_rawlib.basecaller.bam ${outputBAM}/${run}/bam/${sampleID}_rawlib.basecaller.bam

else
    log "INFO" " No RNA bam file for ${sampleID}"
fi

log "INFO" " Creating run directory on ${SharePoint}"
curl --ntlm -u "${username}:${password}" -X MKCOL "${SharePoint}/${run}" -k
    
log "INFO" " Creating ${sampleID}, Generated_Report, and Final_Report directories on ${SharePoint}"
curl --ntlm -u "${username}:${password}" -X MKCOL "${SharePoint}/${run}/${sampleID}" -k
curl --ntlm -u "${username}:${password}" -X MKCOL "${SharePoint}/${run}/${sampleID}/Generated_Report" -k
curl --ntlm -u "${username}:${password}" -X MKCOL "${SharePoint}/${run}/${sampleID}/Generated_Report/Final_Report" -k