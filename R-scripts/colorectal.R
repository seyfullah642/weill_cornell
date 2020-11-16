library("openxlsx")
library(ggplot2)


######## OS genomic data ########

setwd("/Users/sir2013/Documents/CRC/")
#crc_os_old = load(file = "R-objects/crc_os.Rda")
sharepoint_clinical = read.csv("18.02.14-Updated-NGS-CRC-Specimen-Database.csv")
cbioportal_clinical = read.delim("EIPM/EIPM_COLORECTAL_clinical_data.tsv", header = TRUE, sep = "\t")
eipm_clincial_all = read.delim("/Users/sir2013/Documents/cbio-data-new-deployment/EIPM_ALL/data_clinical.txt", header = TRUE, sep = "\t")

#dedup.os.months = subset(os.months,!duplicated(os.months$PMID))
#dedup.os.months$SURVIVAL.STAGE.IV = round(dedup.os.months$SURVIVAL.STAGE.IV)
overlap = subset(sharepoint_clinical, PM.ID %in% cbioportal_clinical$PMID)

df = sharepoint_clinical[as.character(sharepoint_clinical$PM.ID) %in% as.character(eipm_clincial_all$PMID),]

eipm_all_overlap = subset(sharepoint_clinical, toString(PM.ID) %in% toString(eipm_clincial_all$PMID))

non_overlap = subset(sharepoint_clinical, !(PM.ID %in% cbioportal_clinical$PMID))
#short_term_os = subset(dedup.os.months, SURVIVAL.STAGE.IV <= 18)
#long_term_os = subset(dedup.os.months, SURVIVAL.STAGE.IV >= 40)

ggplot(dedup.os.months, aes(SURVIVAL.STAGE.IV)) +
  geom_histogram() + 
  xlab("# of months") + ylab("# of patients") +
  ggtitle("CRC Patient Overall Survival Stage IV") +
  geom_vline(xintercept = 12.75) + geom_vline(xintercept = 25.50) +
  scale_x_continuous(breaks = seq(0, 60, by = 5)) +
  ggsave("Overall Survival Stage IV genomic data", device = "pdf")

crc_quantile = quantile(dedup.os.months$SURVIVAL.STAGE.IV)

######## OS population data ########

setwd("/Users/sir2013/Documents/CRC/")

csv = read.csv("18.02.14-Updated-NGS-CRC-Specimen-Database_filtered.csv")

csv$SURVIVAL.STAGE.IV = csv$SURVIVAL.STAGE.IV / 30.5
csv$SURVIVAL.STAGE.IV = round(csv$SURVIVAL.STAGE.IV)
months = data.frame(csv$PM.ID,csv$SURVIVAL.STAGE.IV)
colnames(months) = c("PMID","OS.months")

setwd("/Users/sir2013/Documents/CRC/R-object")

saveRDS(months, file = "R-objects/crc_os.RDS")
os.months = readRDS(file = "R-objects/crc_os.RDS")

crc_quantile = quantile(csv$SURVIVAL.STAGE.IV)

ggplot(months, aes(months$OS.months)) +
  geom_histogram() + 
  xlab("# of months") + ylab("# of patients") +
  ggtitle("CRC Patient Overall Survival Stage IV") +
  geom_vline(xintercept = 18.25) + geom_vline(xintercept = 38.75) +
  scale_x_continuous(breaks = seq(0, 140, by = 10)) +
  ggsave("Overall Survival Stage IV population data", device = "pdf")


#######################
data_mutation = read.table("data_mutation_extended.txt", header = TRUE, sep = "\t")
data_clinical = read.table("data_clinical.txt", header = TRUE, sep = "\t")

#long term survival
lts = c("PM1050", "PM584", "PM814", "PM860", "PM895", "PM789")

data_mutation$VAF = (100 * (data_mutation$t_alt_count / (data_mutation$t_alt_count + data_mutation$t_ref_count)))

data_clinical$Long_term_survival = "FALSE"
data_clinical$Long_term_survival = ifelse(grepl(paste(lts, collapse = "|"), data_clinical$SAMPLE_ID), "TRUE","FALSE")

longTermSurvival = subset(data_clinical, data_clinical$Long_term_survival == "TRUE")
shortTermSurvival = subset(data_clinical, data_clinical$Long_term_survival == "FALSE")

nras = subset(data_mutation, data_mutation$Hugo_Symbol == "NRAS")
kras = subset(data_mutation, data_mutation$Hugo_Symbol == "KRAS")
braf = subset(data_mutation, data_mutation$Hugo_Symbol == "BRAF")

df_nras = data.frame(nras$Hugo_Symbol, nras$Tumor_Sample_Barcode, nras$HGVSp_Short)
colnames(df_nras)[2] = "Tumor_sample_Barcode"
df_nras$tmb = "NA"
df_nras$msi = "NA"
df_nras$clonet = "NA"
df_nras$vaf = "NA"
df_nras$Long_term_survival = "FALSE"

df_nras$Long_term_survival = ifelse(grepl(paste(lts, collapse = "|"), df_nras$Tumor_sample_Barcode), "TRUE","FALSE")

df_kras = data.frame(kras$Hugo_Symbol, kras$Tumor_Sample_Barcode, kras$HGVSp_Short)
colnames(df_kras)[2] = "Tumor_sample_Barcode"
df_kras$tmb = "NA"
df_kras$msi = "NA"
df_kras$clonet = "NA"
df_kras$vaf = "NA"
df_kras$Long_term_survival = "FALSE"

df_kras$Long_term_survival = ifelse(grepl(paste(lts, collapse = "|"), df_kras$Tumor_sample_Barcode), "TRUE","FALSE")

df_braf = data.frame(braf$Hugo_Symbol, braf$Tumor_Sample_Barcode, braf$HGVSp_Short)
colnames(df_braf)[2] = "Tumor_sample_Barcode"
df_braf$tmb = "NA"
df_braf$msi = "NA"
df_braf$clonet = "NA"
df_braf$vaf = "NA"
df_braf$Long_term_survival = "FALSE"

df_braf$Long_term_survival = ifelse(grepl(paste(lts, collapse = "|"), df_braf$Tumor_sample_Barcode), "TRUE","FALSE")

#for(i in 1:nrow(data_clinical)){

#nras
for(k in 1:nrow(df_nras)){

  for(i in 1:nrow(data_clinical)){
    
    if(toString(data_clinical[i,1]) %in% toString(df_nras[k,2])){
      df_nras[k,4] = data_clinical[i,14]
      df_nras[k,5] = data_clinical[i,15]
      df_nras[k,6] = data_clinical[i,4]
    }
  }
  
  for(i in 1:nrow(data_mutation)){
    
    if(toString(data_mutation[i,15]) %in% toString(df_nras[k,2])){
      df_nras[k,7] = format(round(data_mutation[i,23], 2), nsmall = 2)
    }
  }
}
  
#kras
for(k in 1:nrow(df_kras)){

  for(i in 1:nrow(data_clinical)){
    
    if(toString(data_clinical[i,1]) %in% toString(df_kras[k,2])){
      df_kras[k,4] = data_clinical[i,14]
      df_kras[k,5] = data_clinical[i,15]
      df_kras[k,6] = data_clinical[i,4]
    }
  }
  
  for(i in 1:nrow(data_mutation)){
    
    if(toString(data_mutation[i,15]) %in% toString(df_kras[k,2])){
      df_kras[k,7] = format(round(data_mutation[i,23], 2), nsmall = 2)
    }
  }
}
  
#braf
for(k in 1:nrow(df_braf)){

  for(i in 1:nrow(data_clinical)){
    
    if(toString(data_clinical[i,1]) %in% toString(df_braf[k,2])){
      df_braf[k,4] = data_clinical[i,14]
      df_braf[k,5] = data_clinical[i,15]
      df_braf[k,6] = data_clinical[i,4]
    }
  }
  
  for(i in 1:nrow(data_mutation)){
    
    if(toString(data_mutation[i,15]) %in% toString(df_braf[k,2])){
      df_braf[k,7] = format(round(data_mutation[i,23], 2), nsmall = 2)
    }
  }
}

#print(subset(df_nras, df_nras$Long_term_survival == "TRUE"))
lts_kras = subset(df_kras, df_kras$Long_term_survival == "TRUE")
lts_braf = subset(df_braf, df_braf$Long_term_survival == "TRUE")

df_lts = merge(lts_braf, lts_kras, all = TRUE)
write.csv(df_lts, file = "Long_term_survival.csv")

sts_kras = subset(df_kras, df_kras$Long_term_survival == "FALSE")
sts_braf = subset(df_braf, df_braf$Long_term_survival == "FALSE")

df_sts = merge(sts_braf, sts_kras, all = TRUE)
df_sts = merge(df_sts, df_nras, all = TRUE)

mat = matrix(c(4,27,2,47), 2,2)
output = fisher.test(mat)

#### MSK OS MONTHS ####

setwd("/Users/sir2013/Documents/CRC/MSK")

data = read.table("crc_msk_2017_clinical_data.tsv", header = TRUE, sep = "\t")

df = data[which(data$Stage.At.Diagnosis == "IV"),]
df = df[which(df$Overall.Survival..Months. != "NA"),]
os_months = as.data.frame(round(df$Overall.Survival..Months.))
colnames(os_months) = c("OS.months")

ggplot(os_months, aes(os_months$OS.months)) +
  geom_histogram() + 
  xlab("# of months") + ylab("# of patients") +
  ggtitle("MSKCC Patient Overall Survival Stage IV") +
  geom_vline(xintercept = 17) + geom_vline(xintercept = 48) +
  ggsave("MSKCC Overall Survival stage IV", device = "pdf")

os_months_quantile = quantile(os_months$OS.months)

os_months_quantile


######## TCGA OS MONTHS ########

setwd("/Users/sir2013/Documents/CRC/TCGA")

data = read.table("coadread_tcga_pub_clinical_data.tsv", header = TRUE, sep = "\t")

df = data[which((data$Tumor.Stage.2009 %in% "Stage IV") | (data$Tumor.Stage.2009 %in% "Stage IVA")),]

os_months_quantile = quantile(df$Overall.Survival..Months.)

# attributes(os_months_quantile)
# names(os_months_quantile)
os_months_quantile

ggplot(df, aes(Overall.Survival..Months.)) +
  geom_histogram() + 
  xlab("# of months") + ylab("# of patients") +
  ggtitle("TCGA Patient Overall Survival Stage IV & IVA") +
  geom_vline(xintercept = 1.020) + geom_vline(xintercept = 12.475) +
  ggsave("TCGA Overall Survival stage IV & IVA", device = "pdf")


######## CURL COMMAND ########
#system(paste0("curl --ntlm -u '",read.table("config",stringsAsFactors = F)[1,1],":",read.table("config",stringsAsFactors = F)[2,1], "' -o ",getwd(),
#             "/tmp_clinical_rcc.xlsx https://sharepoint.weill.cornell.edu/sites/ipm/comp/Shared%20Documents/EIPM%20RCC/2019-3-8__WCMC-RCC-database-sample-labels.xlsx"),
#intern=T)




