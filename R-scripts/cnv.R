library(ggplot2)
library(openxlsx)


setwd("/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine")

scna=read.xlsx( "Oncomine_EXaCT-1_CNV.xlsx")

scna_subset = subset(scna, scna$Data.Type != "Research") #& scna$Clonet.Tumor.Content != 0.851)
scna_discordant = subset(scna_subset, scna_subset$exact1.log2.ratio <= 0.5 & scna_subset$exact1.log2.ratio >= -0.5)

plot(log2(scna$RAW_CN), scna$exact1.log2.ratio )

cor.test( log2(scna$RAW_CN+0.00000001), as.numeric(scna$exact1.log2.ratio) )
cor.test( log2(scna_subset$RAW_CN+0.00000001), as.numeric(scna_subset$exact1.log2.ratio) )

ggplot(scna, aes(x=log2(RAW_CN+0.00000001), y=as.numeric(exact1.log2.ratio), color=Oncomine.CNV)) + geom_point() +
  geom_hline(yintercept = -0.5, linetype="dashed", show.legend = F) +
  geom_hline(yintercept = 0.5, linetype="dashed", show.legend = F) + 
  geom_hline(yintercept = -1, linetype="solid", col="blue", show.legend = F) +
  geom_hline(yintercept = 1, linetype="solid", col="red", show.legend = F) +
  geom_vline(xintercept = log2(1), linetype="dashed", col="blue", show.legend = F) +
  geom_vline(xintercept = log2(3), linetype="dashed", col="red", show.legend = F) +
  scale_x_continuous(limits = c(-7, 7)) +
  scale_fill_discrete(name = "Oncomine")
  

ggplot(scna_subset, aes(x=log2(RAW_CN+0.00000001), y=as.numeric(exact1.log2.ratio), color=Oncomine.CNV)) + geom_point() +
  geom_hline(yintercept = -0.5, linetype="dashed", show.legend = F) +
  geom_hline(yintercept = 0.5, linetype="dashed", show.legend = F) +
  geom_hline(yintercept = -1, linetype="solid", col="blue", show.legend = F) +
  geom_hline(yintercept = 1, linetype="solid", col="red", show.legend = F) +
  geom_vline(xintercept = log2(1), linetype="dashed", col="blue", show.legend = F) +
  geom_vline(xintercept = log2( 3 ), linetype="dashed", col="red", show.legend = F) +
  scale_x_continuous(limits = c(-7, 7))

ggplot(scna_discordant, aes(x=log2(RAW_CN+0.00000001), y=as.numeric(exact1.log2.ratio), color=Oncomine.CNV)) + geom_point() +
  geom_hline(yintercept = -0.5, linetype="dashed", show.legend = F) +
  geom_hline(yintercept = 0.5, linetype="dashed", show.legend = F) +
  geom_hline(yintercept = -1, linetype="solid", col="blue", show.legend = F) +
  geom_hline(yintercept = 1, linetype="solid", col="red", show.legend = F) +
  geom_vline(xintercept = log2(1), linetype="dashed", col="blue", show.legend = F) +
  geom_vline(xintercept = log2( 3 ), linetype="dashed", col="red", show.legend = F) +
  scale_x_continuous(limits = c(-7, 7)) +
  scale_y_continuous(limits = c(-3.5,3.5))

scna[ sort.list(scna_subset$exact1.log2.ratio, decreasing = F), ]

table( scna_subset$Oncomine.CNV, scna_subset$`exact1.LOSS/DEL/GAIN/AMP`)

chisq.test( scna_subset$Oncomine.CNV, scna_subset$`exact1.LOSS/DEL/GAIN/AMP`)
