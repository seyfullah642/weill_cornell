#!/bin/bash

source /oncorseq-bot/scripts/config.cfg

#ANNOTATION IN PROGRESS update
${limsapi}
wait
${phase1phase2}
wait
sleep 2m

#READY FOR REVIEW update
${readyForReview}
wait
rm ${tmpdir}/*.txt
