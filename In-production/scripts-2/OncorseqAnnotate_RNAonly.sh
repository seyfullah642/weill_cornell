SampleName=$1
BamName=$2
SharePoint=$3
run=$4

cd /input

export firstvcf=$(find `pwd` -name '*_v1*vcf')

rsync -av $firstvcf /opt/$SampleName.vcf

cd /opt

rsync -av /input3/*.xlsx /opt/

python transform.py /opt /opt/$SampleName.xls
python Dockerized_HyperLinks_RNAonly.py $SampleName.xls ${run}
python uploadtoSharepoint.py $SharePoint/$run/$BamName/Generated_Report/ ${SampleName}_final.xlsx

rsync -av /opt/*_final.xlsx /output
