#!/bin/bash

vcf=$1
resources=$2

cat ${vcf} | $vcftools_dir/vcf-sort > tmp.vcf
wait

java -Xmx2500m -jar $snpeff_dir/SnpSift.jar dbnsfp -db ${resources}/dbNSFP3.5.txt.gz -a -f 1000Gp3_AF,ExAC_AF,clinvar_rs ./tmp.vcf > ${vcf}.ann.vcf
