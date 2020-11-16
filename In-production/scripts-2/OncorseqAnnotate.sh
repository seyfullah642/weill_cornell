SampleName=$1
BamName=$2
SharePoint=$3
run=$4

export samtools_dir
export bcftools_dir

cd /input

export firstvcf=$(find `pwd` -name '*_v1*vcf')

rsync -av $firstvcf /opt/$SampleName.vcf

cd /opt

bash dockerized_annotate_vcf.sh /opt/$SampleName.vcf
python Dockerized_mpileup.v2.py /input2/${BamName}.rawlib.bam --shell_dir /opt/
bash /opt/mpileup_Oncomine*.sh

rsync -av $(find /input/ -name '*.vcf') /opt/
rsync -av /input3/*.xlsx /opt/

python Dockerized_transform_v2.py /opt /opt/$SampleName.xls

rsync -av /opt/*.extendedAnn.xls /output/

python Dockerized_HyperLinks.py $SampleName.xls.extendedAnn.xls ${run}
python uploadtoSharepoint.py $SharePoint/$run/$BamName/Generated_Report/ ${BamName}_v1_final.xlsx

rsync -av /opt/*_final.xlsx /output
