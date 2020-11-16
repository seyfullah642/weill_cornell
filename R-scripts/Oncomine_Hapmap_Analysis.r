library('GenomicRanges')
exact1_gene_list = t(read.table('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/EXaCT1.Gene.clinically.relevant.list.txt'))
position_based_relevance = read.table('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/results.table.txt')
chroms = c()
starts = c()
widths = c()
position_based_relevance[,3] = as.vector(position_based_relevance[,3])
for(i in 1:nrow(position_based_relevance)){
	split1 = strsplit(position_based_relevance[i,3],":")[[1]]
	split2 = strsplit(split1[2],"-")[[1]]
	chroms = c(chroms,split1[1])
	starts = c(starts,as.numeric(split2[1]))
	widths = c(widths,as.numeric(split2[2])-as.numeric(split2[1])+1)
}
position_based_relevance_gr = GRanges(seqnames=Rle(chroms),IRanges(start=starts,width=widths))

# amplicon coverage files
files = c ('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-10_v2_541b2b74-a5d2-4c6a-9c8d-fd06c9579452_2018-06-19_10-40-32-546_All/QC/HAPMAP12878-10_v2/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-1_v1_5a2d6e79-f81a-4c21-8995-b067f0d716ca_2018-06-19_10-41-09-372_All/QC/HAPMAP12878-1_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-2_v1_60cc926e-c8f3-433e-be8d-24680c7d3c04_2018-06-19_10-41-06-246_All/QC/HAPMAP12878-2_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-3_v1_134b958c-8119-49b6-aa73-09bce487dd33_2018-06-19_10-41-02-825_All/QC/HAPMAP12878-3_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-4_v2_bb92b991-021e-44ec-b39f-f9838170daa3_2018-06-19_10-40-29-248_All/QC/HAPMAP12878-4_v2/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-5_v2_1f77529e-7891-4222-ae5f-2c40aa247f8e_2018-06-19_10-40-26-104_All/QC/HAPMAP12878-5_v2/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-6_v2_1028c43d-4c1b-41c6-aa58-e05b3c21c787_2018-06-19_10-40-22-492_All/QC/HAPMAP12878-6_v2/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-7_v2_50705b48-0bfb-49cf-b515-bb0f88422e72_2018-06-19_10-40-19-334_All/QC/HAPMAP12878-7_v2/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-8_v2_375bced9-d844-4ced-9d17-9f8ed99fb800_2018-06-19_10-40-16-851_All/QC/HAPMAP12878-8_v2/StatsActor/amplicons_low_no_coverage_statistics.txt','/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-9_v2_b4629a23-585f-4084-a440-49e7ee250e11_2018-06-19_10-40-35-842_All/QC/HAPMAP12878-9_v2/StatsActor/amplicons_low_no_coverage_statistics.txt')
################################
my_summary_table = c()
my_low_amplicons = c()
for( i in 1:length(files)){
	file_split = strsplit(files[i],"/")[[1]]
	sample_name = file_split[length(file_split)-2]
	# read in table
	t = read.delim(files[i])
	t_low = t[t$Avg<400,]
	# Store summary results
	perc_low = 100 * sum(t$Avg<400)/nrow(t)
	summary_line = c(sample_name,as.numeric(sum(t$Avg<400)),as.numeric(nrow(t)),sprintf("%3.2f",perc_low))
	my_summary_table = rbind(my_summary_table,summary_line)
	colnames(my_summary_table)  = c('Sample_Name','Low_Covered_Amplicons','Total_Amplicons','Percent_Amplicons_Low')
	rownames(my_summary_table) = c()
	# store table
	Pos_key = paste(t_low$Region,":",t_low$Start,"-",t_low$End,sep="")
	t_low$X.Id = Pos_key
	t_low = cbind(t_low,rep(sample_name,nrow(t_low)))
	headers = colnames(t_low)
	headers[length(headers)] = "Sample_Name"
	colnames(t_low) <- headers
	my_low_amplicons = rbind(my_low_amplicons,t_low)
}

#
write.table(my_summary_table,'/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/Oncomine_Hapmap.Low_Cov_Amplicon.Summary.txt',quote=F,row.names=F,sep="\t")

#
#write.table(my_low_amplicons,'Oncomine_Hapmap.Low_Cov_Amplicon.All.txt',quote=F,row.names=F,sep="\t")


pdf('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/Oncomine.Low_Coverage_Amplicon_Distribution.Hapmap.pdf')
hist(Rle(sort(my_low_amplicons$X.Id))@lengths,xlab="Number of Hapmap Samples found in",ylab="Number of Amplicons",main="Low Coverage Amplicon distribution amongst Hapmap samples")
dev.off()

my_table = c()
for(k in 1:10){
	my_table = rbind(my_table,c(k,sum(Rle(sort(my_low_amplicons$X.Id))@lengths==k)))
}
pdf('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/Oncomine.Low_Coverage_Amplicon_Distribution.Hapmap.pdf')
barplot(my_table[,2],names.arg=my_table[,1],ylab="Number of Amplicons",xlab="Number of HAPMAP samples observed",ylim=c(0,400),main='Distribution of Low Coverage [ < 400X ] Oncomine Amplicons')
dev.off()

# ordered list of most commmon amplicons
low_cov_amplicon_table = cbind(Rle(sort(my_low_amplicons$X.Id))@values,Rle(sort(my_low_amplicons$X.Id))@lengths)
colnames(low_cov_amplicon_table) = c('Amplicon Region',"Frequency < 400x Average Coverage in Hapmap Cohort")
low_cov_amplicon_table[,2] = as.numeric(as.character(low_cov_amplicon_table[,2]))
low_cov_amplicon_table = low_cov_amplicon_table[order(as.numeric(as.character(low_cov_amplicon_table[,2])),decreasing=TRUE),]
chroms = c()
starts = c()
widths = c()
for(k in 1:length(low_cov_amplicon_table[,1])){
	split1 = strsplit(low_cov_amplicon_table[k,1],":")[[1]]
	split2 = strsplit(split1[2],"-")[[1]]
	chroms = c(chroms,split1[1])
	starts = c(starts,as.numeric(split2[1]))
	widths = c(widths,as.numeric(split2[2])-as.numeric(split2[1])+1)
}

low_cov_amplicon_gr = GRanges(seqnames=Rle(chroms),IRanges(start=starts,width=widths))

# find gene, regions overlap ....

amplicon_bed = read.table("/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/amplicons.bed",sep= "\t")
gene = unlist(strsplit(as.character(amplicon_bed$V8), ";"))
genes = grep("GENE_ID", gene, value = TRUE)
gene_name = unlist(strsplit(as.character(gene[1]),"="))
gene_names  = grep("[^GENE_ID]", genez, value = TRUE)

Oncomine_Genes_file = read.delim('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/batch_analysis_results_2018-06-19_10-41-12-078_All/HAPMAP12878-1_v1_5a2d6e79-f81a-4c21-8995-b067f0d716ca_2018-06-19_10-41-09-372_All/QC/HAPMAP12878-1_v1/StatsActor/amplicons_low_no_coverage_statistics.txt')
Oncomine_Genes_gr = GRanges(seqnames=Rle(Oncomine_Genes_file$Region),IRanges(start=Oncomine_Genes_file$Start,width=Oncomine_Genes_file$End-Oncomine_Genes_file$Start+1),metadata=gene_names)
#########

position_hit_index = unique(findOverlaps(low_cov_amplicon_gr,position_based_relevance_gr)@from)#@queryHits
gene_hits = intersect(as.vector(exact1_gene_list),as.vector(subsetByOverlaps(Oncomine_Genes_gr,low_cov_amplicon_gr)$metadata))
gene_hit_index = unique(findOverlaps(low_cov_amplicon_gr,Oncomine_Genes_gr[(elementMetadata(Oncomine_Genes_gr)[,1] %in% gene_hits)])@from)#@queryHits
conditions_subset = is.element(1:nrow(low_cov_amplicon_table),gene_hit_index) | is.element(1:nrow(low_cov_amplicon_table),position_hit_index)

low_cov_amplicon_table = cbind(low_cov_amplicon_table,conditions_subset)
header1 = colnames(low_cov_amplicon_table)
header1[length(header1)] = "Contains EXaCT1 Tier1 Alteration"
colnames(low_cov_amplicon_table) <- header1

write.table(low_cov_amplicon_table,'/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/Oncomine_Hapmap.Low_Cov_Amplicon.ClinicalRelevance.txt',quote=F,row.names=F,sep="\t")
write.table(my_low_amplicons,'/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/HAPMAP/Oncomine_Hapmap.Low_Cov_Amplicon.All.txt',quote=F,row.names=F,sep="\t")

########
#STOP HERE
# amplicon coverage files
files = c ('Downloads/FW__Hapmap_results/analysis_HAPMAP12878-4_v1_34202d60-3c60-41bd-b5ed-9baac46ea94a_unfiltered_results_2016-09-19\ 17-58/QC/HAPMAP12878-4_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','Downloads/FW__Hapmap_results/analysis_HAPMAP12878-5_v1_8903ce5b-8629-48f8-8dcb-1c9329057c4f_unfiltered_results_2016-09-19\ 17-57/QC/HAPMAP12878-5_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','Downloads/FW__Hapmap_results/analysis_HAPMAP12878-6_v1_bb0b8f4a-b71f-433b-9b0c-ad70b64b29d1_unfiltered_results_2016-09-19\ 17-57/QC/HAPMAP12878-6_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','Downloads/FW__Hapmap_results/analysis_HAPMAP12878-7_v1_3fd987b1-b4bc-47f8-88ee-b57b1b25ef97_unfiltered_results_2016-09-19\ 17-55/QC/HAPMAP12878-7_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','Downloads/FW__Hapmap_results/analysis_HAPMAP12878-10_v1_822b277d-fd8d-4868-89ee-eeb9bc7397e2_unfiltered_results_2016-09-19\ 17-54/QC/HAPMAP12878-10_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','Downloads/FW__Hapmap_results/analysis_HAPMAP12878-9_v1_d8e610fb-4efd-4a1d-9979-261c08186707_unfiltered_results_2016-09-19\ 17-54/QC/HAPMAP12878-9_v1/StatsActor/amplicons_low_no_coverage_statistics.txt','Downloads/FW__Hapmap_results/analysis_HAPMAP12878-8_v1_8e1b3650-b259-4a90-b783-76f79e9ea06d_unfiltered_results_2016-09-19\ 17-42/QC/HAPMAP12878-8_v1/StatsActor/amplicons_low_no_coverage_statistics.txt')
################################
my_summary_table = c()
my_low_amplicons = c()
for( i in 1:length(files)){
	file_split = strsplit(files[i],"/")[[1]]
	sample_name = file_split[length(file_split)-2]
	# read in table
	t = read.delim(files[i])
	t_low = t[t$Avg<400,]
	# Store summary results
	perc_low = 100 * sum(t$Avg<400)/nrow(t)
	summary_line = c(sample_name,as.numeric(sum(t$Avg<400)),as.numeric(nrow(t)),sprintf("%3.2f",perc_low))
	my_summary_table = rbind(my_summary_table,summary_line)
	colnames(my_summary_table)  = c('Sample_Name','Low_Covered_Amplicons','Total_Amplicons','Percent_Amplicons_Low')
	rownames(my_summary_table) = c()
	# store table
	Pos_key = paste(t_low$Region,":",t_low$Start,"-",t_low$End,sep="")
	t_low$X.Id = Pos_key
	t_low = cbind(t_low,rep(sample_name,nrow(t_low)))
	headers = colnames(t_low)
	headers[length(headers)] = "Sample_Name"
	colnames(t_low) <- headers
	my_low_amplicons = rbind(my_low_amplicons,t_low)
}

#
write.table(my_summary_table,'Oncomine_Hapmap.Low_Cov_Amplicon.Summary.1.txt',quote=F,row.names=F,sep="\t")

#
#write.table(my_low_amplicons,'Oncomine_Hapmap.Low_Cov_Amplicon.All.txt',quote=F,row.names=F,sep="\t")


#pdf('Oncomine.Low_Coverage_Amplicon_Distribution.Hapmap.pdf')
#hist(Rle(sort(my_low_amplicons$X.Id))@lengths,xlab="Number of Hapmap Samples found in",ylab="Number of Amplicons",main="Low Coverage Amplicon distribution amongst Hapmap samples")
#dev.off()

my_table = c()
for(k in 1:7){
	my_table = rbind(my_table,c(k,sum(Rle(sort(my_low_amplicons$X.Id))@lengths==k)))
}
pdf('Oncomine.Low_Coverage_Amplicon_Distribution.Hapmap.1.pdf')
barplot(my_table[,2],names.arg=my_table[,1],ylab="Number of Amplicons",xlab="Number of HAPMAP samples observed",ylim=c(0,max(my_table[,2])),main='Distribution of Low Coverage [ < 400X ] Oncomine Amplicons')
dev.off()

# ordered list of most commmon amplicons
low_cov_amplicon_table = cbind(Rle(sort(my_low_amplicons$X.Id))@values,Rle(sort(my_low_amplicons$X.Id))@lengths)
colnames(low_cov_amplicon_table) = c('Amplicon Region',"Frequency < 400x Average Coverage in Hapmap Cohort")
low_cov_amplicon_table[,2] = as.numeric(as.character(low_cov_amplicon_table[,2]))
low_cov_amplicon_table = low_cov_amplicon_table[order(as.numeric(as.character(low_cov_amplicon_table[,2])),decreasing=TRUE),]
chroms = c()
starts = c()
widths = c()
for(k in 1:length(low_cov_amplicon_table[,1])){
	split1 = strsplit(low_cov_amplicon_table[k,1],":")[[1]]
	split2 = strsplit(split1[2],"-")[[1]]
	chroms = c(chroms,split1[1])
	starts = c(starts,as.numeric(split2[1]))
	widths = c(widths,as.numeric(split2[2])-as.numeric(split2[1])+1)
}

low_cov_amplicon_gr = GRanges(seqnames=Rle(chroms),IRanges(start=starts,width=widths))

# find gene, regions overlap ....
Oncomine_Genes_file = read.delim('Downloads/FW__Hapmap_results/analysis_HAPMAP12878-1_v1_5a2d6e79-f81a-4c21-8995-b067f0d716ca_unfiltered_results_2016-09-19\ 17-58/QC/HAPMAP12878-1_v1/StatsActor/genes_low_no_coverage_statistics.txt')
Oncomine_Genes_gr = GRanges(seqnames=Rle(Oncomine_Genes_file$Region),IRanges(start=Oncomine_Genes_file$Start,width=Oncomine_Genes_file$End-Oncomine_Genes_file$Start+1),metadata=Oncomine_Genes_file$X.Id)
#########

position_hit_index = unique(findOverlaps(low_cov_amplicon_gr,position_based_relevance_gr)@queryHits)
gene_hits = intersect(as.vector(exact1_gene_list),as.vector(subsetByOverlaps(Oncomine_Genes_gr,low_cov_amplicon_gr)$metadata))
gene_hit_index = unique(findOverlaps(low_cov_amplicon_gr,Oncomine_Genes_gr[(elementMetadata(Oncomine_Genes_gr)[,1] %in% gene_hits)])@queryHits)
conditions_subset = is.element(1:nrow(low_cov_amplicon_table),gene_hit_index) | is.element(1:nrow(low_cov_amplicon_table),postion_hit_index)

low_cov_amplicon_table = cbind(low_cov_amplicon_table,conditions_subset)
header1 = colnames(low_cov_amplicon_table)
header1[length(header1)] = "Contains EXaCT1 Tier1 Alteration"
colnames(low_cov_amplicon_table) <- header1

write.table(low_cov_amplicon_table,'Oncomine_Hapmap.Low_Cov_Amplicon.ClinicalRelevance.1.txt',quote=F,row.names=F,sep="\t")
write.table(my_low_amplicons,'Oncomine_Hapmap.Low_Cov_Amplicon.All.1.txt',quote=F,row.names=F,sep="\t")