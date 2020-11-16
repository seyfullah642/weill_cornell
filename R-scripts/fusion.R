library(ggplot2)
library(xlsx)

setwd("/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/")

fusion_data = read.table("Fusion_Data.txt", header = TRUE)
bin1 = subset(fusion_data, fusion_data$FILTER == "PASS" & fusion_data$Read_Count > 20 & fusion_data$Read_Count <= 64)
bin2 = subset(fusion_data, fusion_data$FILTER == "PASS" & fusion_data$Read_Count > 64 & fusion_data$Read_Count <= 512)
bin3 = subset(fusion_data, fusion_data$FILTER == "PASS" & fusion_data$Read_Count > 512)

#colSums(fusion_read_count$Read_Count != 0)

ggplot(bin1, aes(x=Read_Count)) + geom_density()
ggplot(bin2, aes(x=Read_Count)) + geom_density()
ggplot(bin3, aes(x=Read_Count)) + geom_density()
