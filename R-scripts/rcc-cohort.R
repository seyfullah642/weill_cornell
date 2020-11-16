library(ggplot2)
require(maftools)
library(ggrepel)
library(openxlsx)

#### FIRST ANALYSIS ####

setwd("/Users/sir2013/Documents/RCC/outputs")

ipm_gene_mut_count = read.delim("sample_gene_count_rcc_eipm.txt",header = TRUE, sep = "\t")
tcga_gene_mut_count = read.delim("sample_gene_count_rcc_tcga.txt",header = TRUE, sep = "\t")

ipm_gene_cnv_count = read.delim("sample_gene_cnv_count_rcc_eipm.txt",header = TRUE, sep = "\t")
tcga_gene_cnv_count = read.delim("sample_gene_cnv_count_rcc_tcga.txt",header = TRUE, sep = "\t")


drop = c("X")
ipm_gene_mut_count = ipm_gene_mut_count[,!(names(ipm_gene_mut_count) %in% drop)]
ipm_gene_cnv_count = ipm_gene_mut_count[,!(names(ipm_gene_cnv_count) %in% drop)]
tcga_gene_mut_count = tcga_gene_mut_count[,!(names(tcga_gene_mut_count) %in% drop)]
tcga_gene_cnv_count = tcga_gene_cnv_count[,!(names(tcga_gene_cnv_count) %in% drop)]

gene_names = names(ipm_gene_mut_count)
gene_names = gene_names[gene_names != "Sample_ID"]

print(gene_names)

# EIPM VS TCGA mutations

p_values_mut = c()

for(i in gene_names){
  #print(ipm_gene_mut_count[i])
  ipm_mut_hit = sum(ipm_gene_mut_count[i] > 0)
  ipm_mut_miss = sum(ipm_gene_mut_count[i] == 0)
  
  tcga_mut_hit = sum(tcga_gene_mut_count[i] > 0)
  tcga_mut_miss = sum(tcga_gene_mut_count[i] == 0)
  
  #print(i)
  mat = matrix(c(ipm_mut_hit, ipm_mut_miss, tcga_mut_hit, tcga_mut_miss), 2,2)
  test = fisher.test(mat)
  p_values_mut[i] = test$p.value
} 
#print(p_values_mut)
write.table(as.data.frame(p_values_mut),"EIPMvsTCGA_mut.txt", sep = "\t")

p_values_cna = c()

for(i in gene_names){
  #print(ipm_gene_mut_count[i])
  ipm_cna_hit = sum(ipm_gene_cnv_count[i] > 0)
  ipm_cna_miss = sum(ipm_gene_cnv_count[i] == 0)
  
  tcga_cna_hit = sum(tcga_gene_cnv_count[i] > 0)
  tcga_cna_miss = sum(tcga_gene_cnv_count[i] == 0)
  
  #print(i)
  mat = matrix(c(ipm_cna_hit, ipm_cna_miss, tcga_cna_hit, tcga_cna_miss), 2,2)
  test = fisher.test(mat)
  p_values_cna[i] = test$p.value
} 
#print(p_values_cna)
write.table(as.data.frame(p_values_cna),"EIPMvsTCGA_cna.txt", sep = "\t")

#### SECOND ANALYSIS ####

setwd("/Users/sir2013/Documents/RCC/")

rcc = read.delim("EIPM-TCGA-SATO-RCC-mutated-genes.txt", header = TRUE, sep = "\t")
cc = read.delim("EIPM-TCGA-SATO-CC-mutated-genes.txt", header = TRUE, sep = "\t")

ggplot(rcc, aes(fill=rcc$Cohort, y=as.numeric(sub("%", "", rcc$Freq)), x=rcc$Gene)) + 
  geom_bar(position="dodge", stat="identity") +
  labs(y = "Frequency %", x = "Genes", title = "RCC Cohort Somatic Mutations Comparison") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  guides(fill=guide_legend(title="Cohort")) +
  ggsave(filename = "/Users/sir2013/Documents/Weill_Cornell/RCC/pdf-n-images/RCC.pdf", plot = last_plot())

ggplot(cc, aes(fill=cc$Cohort, y=as.numeric(sub("%", "", cc$Freq)), x=cc$Gene)) + 
  geom_bar(position="dodge", stat="identity") +
  labs(y = "Frequency %", x = "Genes", title = "Clear Cell Cohort Somatic Mutations Comparison") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  guides(fill=guide_legend(title="Cohort")) +
  ggsave(filename = "/Users/sir2013/Documents/Weill_Cornell/RCC/pdf-n-images/CC.pdf", plot = last_plot())

#### THRID ANALYSIS ####

for(i in 1:length(clear_cell$SAMPLE_ID)){
  
  setwd("/Users/sir2013/Documents/RCC/eipm-data/eipm_rcc_cosmic_filtered")
  
  file = read.delim(paste(clear_cell$SAMPLE_ID[i], ".COSMIC.filtered.MAF", sep = ""), header = TRUE, sep = "\t")
  
  file$normal_depth = as.numeric(as.character(file$normal_depth))
  file$tumor_depth = as.numeric(as.character(file$tumor_depth))
  
  file_1 = subset(file, file$normal_depth >= 30 & file$tumor_depth >= 30)
  file_2 = file_1[!grepl("^Silent_Mutation",as.character(file_1$Variant_Classification)),]
  
  file_2$tumorVAF.corrected = as.numeric(sub("%", "", file_2$tumor_vaf)) * (100/as.numeric(clear_cell$CLONET_PURITY[i]))
  new_file = subset(file_2, as.numeric(sub("%", "", file_2$normal_vaf)) < 2 & as.numeric(file_2$tumorVAF.corrected) > 10)
  
  setwd("/Users/sir2013/Documents/RCC/eipm-data/adjusted-clonet-vaf")
  write.table(new_file, paste(clear_cell$SAMPLE_ID[i], ".MAF", sep = ""), sep = "\t", row.names = F)
}

#### FOURTH ANALYSIS ####

setwd("/Users/sir2013/Documents/RCC/eipm-data")

clinical_data = read.delim("ipm-data_clinical.txt", header = TRUE, sep = "\t")

cc_genes = c('SETD2','VHL','KDM5C','PBRM1','MUC4','MED12','TP53','NF2','SPEN','NCOR1','MTOR','MUC16','CSMD3','ARID1A','ZNRF3','FAM47C','NTRK3',
             'ARHGAP5','PTEN','KMT2C')
cc_genes = as.data.frame(cc_genes)

clear_cell = clinical_data[clinical_data$CLEAR.CELL.RCC == "yes",]
prim = subset(clear_cell, clear_cell$PRIMARY.SITE %in% "Kidney" & clear_cell$TISSUE.SITE %in% "Kidney")
met = subset(clear_cell, clear_cell$PRIMARY.SITE %in% "Kidney" & !(clear_cell$TISSUE.SITE %in% "Kidney"))

#metPID = met$PATIENT_ID
metPID = as.data.frame(unique(met$PATIENT_ID))
primPID = as.data.frame(unique(prim$PATIENT_ID))
#metPID = as.data.frame(metPID))

write.table(cc_genes, file = "cc_gnens.txt", quote = FALSE, sep = "\n", row.names = FALSE, col.names = FALSE)
write.table(primPID, file = "primPID.txt", quote = FALSE, sep = "\n", row.names = FALSE, col.names = FALSE)
write.table(metPID, file = "metPID.txt", quote = FALSE, sep = "\n", row.names = FALSE, col.names = FALSE)

non_clear_cell = clinical_data[clinical_data$CLEAR.CELL.RCC == "no",]

wb = loadWorkbook("/Users/sir2013/Documents/RCC/2019-1-17_WCMC-RCC-database-labels_treatment-annotations.xlsx")
tmp = read.xlsx( wb, "Sheet1")

cc_clincal = subset(tmp, tmp$RCC.histology %in% "clear cell")
treated = subset(cc_clincal, cc_clincal$treatment.with.systemic.therapy %in% "Yes")
non_treated = subset(cc_clincal, cc_clincal$treatment.with.systemic.therapy %in% "No")

treatedPID = as.data.frame(unique(treated$sample.ID))
#separate(treated ,treated$sample.ID, into = "NA", sep = "_")
non_treatedPID = non_treated$sample.ID

#merged_clear_cell = paste(clear_cell$SAMPLE_ID,clear_cell$CLONET_PURITY)

######## PFS > 12 PFS < 6 ########

#VEGF TT: PFS <6mo for resistance, PFS>12mo

setwd("/Users/sir2013/Documents/RCC/eipm-data")
data = read.table("eipm_rcc.clonet_corrected.one_sample_per_patient.maf", header = TRUE, sep = "\t")

pfs_gt_12 = read.table("pfs_gt_12.txt", header = TRUE)
pfs_lt_12 = read.table("pfs_lt_6.txt", header = TRUE)

pfs_gt_12_data = as.data.frame(NULL)
pfs_lt_12_data = as.data.frame(NULL)

for(i in 1:nrow(pfs_gt_12)){
  
  tmp = as.data.frame(NULL)
  tmp = subset(data, pfs_gt_12$id[i] == data$Tumor_Sample_Barcode)
  pfs_gt_12_data = rbind(pfs_gt_12_data, as.data.frame(tmp))
  
}

for(i in 1:nrow(pfs_gt_12)){
  
  tmp = as.data.frame(NULL)
  tmp = subset(data, pfs_lt_12$id[i] == data$Tumor_Sample_Barcode)
  pfs_lt_12_data = rbind(pfs_lt_12_data, as.data.frame(tmp))
  
}
#print(nrow(as.data.frame(pfs_lt_12_data$Hugo_Symbol)))

lt_tmp = unique(as.data.frame(pfs_lt_12_data$Hugo_Symbol))
colnames(lt_tmp)[1] = "Gene"
lt_tmp$Count = 0
lt_tmp$Num.of.Samples = 0

for(i in 1:nrow(lt_tmp)){
  sampleID = subset(pfs_lt_12_data, toString(lt_tmp$Gene[i]) == pfs_lt_12_data$Hugo_Symbol) #toString(lt_tmp$Gene[1394])
  
  lt_tmp$Count[i] = length(sampleID$Hugo_Symbol)
  lt_tmp$Num.of.Samples[i] = length(unique(sampleID$Tumor_Sample_Barcode))
}

lt_tmp = lt_tmp[order(-lt_tmp$Count),]
lt_tmp$WO.Num.of.Samples = (11 - as.integer(lt_tmp$Num.of.Samples))

gt_tmp = unique(as.data.frame(pfs_gt_12_data$Hugo_Symbol))
colnames(gt_tmp)[1] = "Gene"
gt_tmp$Count = 0
gt_tmp$Num.of.Samples = 0

for(i in 1:nrow(gt_tmp)){
  #print(lt_tmp$Gene[20])
  sampleID = subset(pfs_gt_12_data, toString(gt_tmp$Gene[i]) == pfs_gt_12_data$Hugo_Symbol)
  
  gt_tmp$Count[i] = length(sampleID$Hugo_Symbol)
  gt_tmp$Num.of.Samples[i] = length(unique(sampleID$Tumor_Sample_Barcode))
}

gt_tmp = gt_tmp[order(-gt_tmp$Count),]
gt_tmp$WO.Num.of.Samples = (16 - as.integer(gt_tmp$Num.of.Samples))

#cbind(lt_tmp, gt_tmp)
merged_data = merge(lt_tmp, gt_tmp, by = "Gene", all = TRUE)
merged_data[is.na(merged_data)] = 0
colnames(merged_data) = c("GENE","LT12.COUNT","LT12.Num.of.Samples.with","LT12.Num.of.Samples.without","GT12.COUNT",
                          "GT12.Num.of.Samples.with", "GT12.Num.of.Samples.without")

merged_data$LT12.Num.of.Samples.without = ifelse(merged_data$LT12.Num.of.Samples.without == 0 & merged_data$LT12.Num.of.Samples.with == 0, 11, merged_data$LT12.Num.of.Samples.without)
merged_data$GT12.Num.of.Samples.without = ifelse(merged_data$GT12.Num.of.Samples.without == 0 & merged_data$GT12.Num.of.Samples.with == 0, 16, merged_data$GT12.Num.of.Samples.without)

merged_data$pvalue = 0
merged_data$odds.ratio = 0

# Fisher Exact Test
# x_new = log2(x) (odds ratio), y_new = -10 * log10(y) (y axis is the p-value)

for(i in 1:nrow(merged_data)){
  
  mat = matrix(c(as.integer(merged_data$LT12.Num.of.Samples.with[i]) , as.integer(merged_data$LT12.Num.of.Samples.without[i]),
                 as.integer(merged_data$GT12.Num.of.Samples.with[i]), as.integer(merged_data$GT12.Num.of.Samples.without[i])), 2)
  
  fet = fisher.test(mat)
  
  merged_data$pvalue[i] = fet$p.value
  merged_data$odds.ratio[i] = fet$estimate
  
}

merged_data$odds.ratio.log2 = log2(merged_data$odds.ratio)
merged_data$pvalue.log10 = -10 * log10(merged_data$pvalue)

gene_list = subset(merged_data, merged_data$odds.ratio.log2 != Inf & merged_data$odds.ratio.log2 != -Inf)
gene_list = gene_list[-c(1),]
#with(gene_list, plot(gene_list$odds.ratio.log2, gene_list$pvalue.log10, pch=16, main="Volcano plot", xlim=c(-5,5), ylim(0,20)))

ggplot(gene_list, aes(x = odds.ratio.log2, y = pvalue.log10)) +
  geom_point(aes(col = pvalue < 0.05)) +
  xlim(c(-5,5)) + ylim(c(0,20)) +
  xlab("Log2(Odds Ratio)") + ylab("-10*Log10(p value)") +
  scale_color_manual(labels = c("Not significant", "Significant"), values=c("black", "red")) +
  geom_text_repel(data=subset(gene_list, pvalue<0.05), aes(label=GENE)) +
  geom_hline(yintercept=(-10*log10(0.05)), color = "black", size=0.5) +
  ggtitle("Altered Genes in RCC (SNV & INDEL)    PFS>12 vs PFS<6") +
  ggsave("PFS-gt-12_vs_PFS-lt-6", device = "pdf")

######## Immunotherapy OS ########

#OS < 25mo (resistance) OS > 31mo (responsive)

setwd("/Users/sir2013/Documents/RCC/eipm-data")
data = read.table("eipm_rcc.clonet_corrected.one_sample_per_patient.maf", header = TRUE, sep = "\t")

setwd("/Users/sir2013/Documents/RCC/immunotherapy")
df = read.xlsx("2019-1-24__treatment-response-OS.xlsx", sheet = 1)

clear_cell = subset(df, df$histology == "clear cell")
clear_cell$precision.medicine.ID = paste("PM", clear_cell$precision.medicine.ID, sep="")
clear_cell$OS__Mets_FU = clear_cell$OS__Mets_FU / 30.5
clear_cell$OS__Mets_FU = round(clear_cell$OS__Mets_FU)

resistance = subset(clear_cell, OS__Mets_FU <= 25)
responsive = subset(clear_cell, OS__Mets_FU >= 31)

resistance_df = as.data.frame(NULL)
responsive_df = as.data.frame(NULL)

# gene = as.data.frame(unique(data$Hugo_Symbol))
# colnames(gene) = "Gene"

for(i in 1:nrow(resistance)){
  
  tmp = as.data.frame(NULL)
  tmp = data[grep(as.name(resistance$precision.medicine.ID[i]),data$Tumor_Sample_Barcode),]
  
  resistance_df = rbind(resistance_df, as.data.frame(tmp))
  
}

resistance_genes = unique(as.data.frame(resistance_df$Hugo_Symbol))
colnames(resistance_genes)[1] = "Gene"
resistance_genes$Count = 0
resistance_genes$Num.of.Samples = 0

for(i in 1:nrow(resistance_genes)){
  
  sampleID = subset(resistance_df, toString(resistance_genes$Gene[i]) == resistance_df$Hugo_Symbol)
  
  resistance_genes$Count[i] = length(sampleID$Hugo_Symbol)
  resistance_genes$Num.of.Samples[i] = length(unique(sampleID$Tumor_Sample_Barcode))
}

resistance_genes = resistance_genes[order(-resistance_genes$Count),]
resistance_genes$WO.Num.of.Samples = (6 - as.integer(resistance_genes$Num.of.Samples))

for(i in 1:nrow(responsive)){
  
  tmp = as.data.frame(NULL)
  tmp = data[grep(as.name(responsive$precision.medicine.ID[i]),data$Tumor_Sample_Barcode),]
  
  responsive_df = rbind(responsive_df, as.data.frame(tmp))
  
}

responsive_genes = unique(as.data.frame(responsive_df$Hugo_Symbol))
colnames(responsive_genes)[1] = "Gene"
responsive_genes$Count = 0
responsive_genes$Num.of.Samples = 0

for(i in 1:nrow(responsive_genes)){
  
  sampleID = subset(responsive_df, toString(responsive_genes$Gene[i]) == responsive_df$Hugo_Symbol)
  
  responsive_genes$Count[i] = length(sampleID$Hugo_Symbol)
  responsive_genes$Num.of.Samples[i] = length(unique(sampleID$Tumor_Sample_Barcode))
}

responsive_genes = responsive_genes[order(-responsive_genes$Count),]
responsive_genes$WO.Num.of.Samples = (13 - as.integer(responsive_genes$Num.of.Samples))

merged_data = merge(responsive_genes, resistance_genes, by = "Gene", all = TRUE)
merged_data[is.na(merged_data)] = 0
colnames(merged_data) = c("Gene","RP.COUNT","RP.Num.of.Samples.with","RP.Num.of.Samples.without","RT.COUNT",
                          "RT.Num.of.Samples.with", "RT.Num.of.Samples.without")

merged_data$RP.Num.of.Samples.without = ifelse(merged_data$RP.Num.of.Samples.without == 0 & merged_data$RP.Num.of.Samples.with == 0, 13, merged_data$RP.Num.of.Samples.without)
merged_data$RT.Num.of.Samples.without = ifelse(merged_data$RT.Num.of.Samples.without == 0 & merged_data$RT.Num.of.Samples.with == 0, 6, merged_data$RT.Num.of.Samples.without)

merged_data$pvalue = 0
merged_data$odds.ratio = 0

# Fisher Exact Test
# x_new = log2(x) (odds ratio), y_new = -10 * log10(y) (y axis is the p-value)

for(i in 1:nrow(merged_data)){

  mat = matrix(c(as.integer(merged_data$RP.Num.of.Samples.with[i]) , as.integer(merged_data$RP.Num.of.Samples.without[i]),
                 as.integer(merged_data$RT.Num.of.Samples.with[i]), as.integer(merged_data$RT.Num.of.Samples.without[i])), 2)

  fet = fisher.test(mat)

  merged_data$pvalue[i] = fet$p.value
  merged_data$odds.ratio[i] = fet$estimate

}

merged_data$odds.ratio.log2 = log2(merged_data$odds.ratio)
merged_data$pvalue.log10 = -10 * log10(merged_data$pvalue)

immunotherapy_genes = subset(merged_data, merged_data$odds.ratio.log2 != Inf & merged_data$odds.ratio.log2 != -Inf)

ggplot(immunotherapy_genes, aes(x = odds.ratio.log2, y = pvalue.log10)) +
  geom_point(aes(col = pvalue < 0.05)) +
  xlim(c(-5,5)) + ylim(c(0,20)) +
  xlab("Log2(Odds Ratio)") + ylab("-10*Log10(p value)") +
  scale_color_manual(labels = c("Not significant", "Significant "), values=c("black", "red")) +
  geom_text_repel(data=subset(immunotherapy_genes, pvalue<0.05), aes(label=Gene)) +
  geom_hline(yintercept=(-10*log10(0.05)), color = "black", size=0.5) +
  ggtitle("Altered Genes in RCC (SNV & INDEL) Im Check Point   OS>31 vs OS<25") +
  ggsave("Immunotherapy_OS", device = "pdf")






#saveRDS(months, file = "R-objects/crc_os.RDS")
rcc_clinical_data =  load(file = "rcc_data/rcc_clinical_data.Rda")

clear.cell.clinical.data = subset(clinical.data, RCC.histology == "clear cell" & 
                                    `best.PFS.VEGF-TT` != "NA")

clear.cell.clinical.data$`best.PFS.VEGF-TT` = as.integer(clear.cell.clinical.data$`best.PFS.VEGF-TT`) / 30.5
clear.cell.clinical.data$`best.PFS.VEGF-TT` = round(clear.cell.clinical.data$`best.PFS.VEGF-TT`)

clear.cell.clinical.data.tmp = subset(clear.cell.clinical.data, !duplicated(PMID))

pfs.gt.12 = subset(clear.cell.clinical.data.tmp, clear.cell.clinical.data.tmp$`best.PFS.VEGF-TT` > 12)
pfs.lt.6 = subset(clear.cell.clinical.data.tmp, clear.cell.clinical.data.tmp$`best.PFS.VEGF-TT` < 6)

clinical.data$PMID














