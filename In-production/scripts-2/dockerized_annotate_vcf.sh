#!/bin/bash

cat $1 | $vcftools_dir/vcf-sort > tmp.vcf
wait

java -Xmx2500m -jar $snpeff_dir/SnpSift.jar dbnsfp -db /resources/dbNSFP3.5.txt.gz -a -f 1000Gp3_AF,ExAC_AF,clinvar_rs ./tmp.vcf > $1.ann.vcf
