library("ggplot2")
options(stringsAsFactors=FALSE)
clia_sensitivity_data=rbind(c(79.2,79.2,"KRAS"),c(16.00,21.47,"KRAS"),c(11.00,12.08,"KRAS"),c(6.7,3.41,"KRAS"),c(3.2,2.02,"KRAS"),c(0.00,0.00,"KRAS"),c(68.7,61.00,"BRAF"),c(18.3,17.44,"BRAF"),c(7.5,7.73,"BRAF"),c(3.3,2.08,"BRAF"),c(0.00,0.00,"BRAF"),c(100.00,100.00,"JAK2"),c(19.4,23.88,"JAK2"),c(8.9,8.13,"JAK2"),c(0.00,0.00,"JAK2"),c(64.5,61.5,"EGFR"),c(14.8,14.94,"EGFR"),c(30.6,28.21,"EGFR"),c(8.7,8.32,"EGFR"),c(0.00,0.00,"EGFR"))
clia_sensitivity_data = as.data.frame(clia_sensitivity_data)
colnames(clia_sensitivity_data) = c("AmpliSeq_VAF","ExACT1_VAF","Alteration_Type")

clia_sensitivity_data$AmpliSeq_VAF = as.numeric(as.character(clia_sensitivity_data$AmpliSeq_VAF))
clia_sensitivity_data$ExACT1_VAF = as.numeric(as.character(clia_sensitivity_data$ExACT1_VAF))
dfid <- data.frame(c1=(0:100),c2=c(0:100))
cor(clia_sensitivity_data$ExACT1_VAF,clia_sensitivity_data$AmpliSeq_VAF,method="pearson")
p = ggplot(clia_sensitivity_data ,aes(x=ExACT1_VAF,y=AmpliSeq_VAF,shape=factor(Alteration_Type),color=factor(Alteration_Type))) + geom_point(size=2,position="jitter") + ylim(0,100) + xlim(0,100) + labs(x="EXaCT-1 Variant Allele Frequency (%)",y="AmpliSeq Variant Allele Frequency (%)")
p = p + ggtitle(expression(atop(textstyle("Variant Allele Frequency:AmpliSeq vs EXaCT-1 CLIA validated alterations"),atop("pearson correlation: 0.9962"))))
p = p + geom_abline(slope=1,intercept=0,linetype=2)
p = p + guides(shape=guide_legend(title="Alteration Type"),color=guide_legend(title="Alteration Type"))
pdf('AmpliSeq_ExACT1.CLIA_Alterations.Mutation_Comparison.Figure8b.pdf')
p +theme(axis.text=element_text(size=16),
        axis.title=element_text(size=12,face="bold"))
dev.off()

png('AmpliSeq_ExACT1.CLIA_Alterations.Mutation_Comparison.Figure8b.png')
p +theme(axis.text=element_text(size=16),
        axis.title=element_text(size=12,face="bold"),plot.title=element_text(size=13,face="bold"))
dev.off()

dfid <- data.frame(c1=(0:35),c2=c(0:35))
her2_data = rbind(c(33.8,3.57),c(18.2,2.74),c(6.2,1.66),c(4.4,1.05),c(3.9,0.60),c(3.5,0.66))
her2_data[,2] = 2^(her2_data[,2]) * 2
her2_data = as.data.frame(her2_data)
pdf('AmpliSeq_ExACT1.CLIA_Alterations.HER2_Copy_Number.Figure8c.pdf')
ggplot(her2_data,aes(y=V1,x=V2)) + geom_point() + geom_line(data=dfid, aes_string(x="c1", y="c2"),color="black",size=0.5,linetype=2) + labs(x="Estimated Copy Number\n(From EXaCT-1 Data)",y="Expected Copy Number\n(from Digital PCR)") + ggtitle(expression(atop("Estimated versus Expected HER2 Copy Number of Validation Samples"),atop("pearson correlation: ",sprintf("%3.4f",cor(her2_data$V1,her2_data$V2,method="pearson")),sep=""))) +theme(axis.text=element_text(size=16),
        axis.title=element_text(size=18,face="bold"),plot.title = element_text(lineheight=.8, face="bold"))
dev.off()

cor_val1 =paste("pearson correlation: ", sprintf("%3.4f",cor(her2_data$V1,her2_data$V2,method="pearson")))
png('AmpliSeq_ExACT1.CLIA_Alterations.HER2_Copy_Number.Figure8c.png')
ggplot(her2_data,aes(y=V1,x=V2)) + geom_point() + geom_line(data=dfid, aes_string(x="c1", y="c2"),color="black",size=0.5,linetype=2) + labs(x="Estimated Copy Number\n(EXaCT-1 Data)",y="Expected Copy Number\n(Digital PCR)") + ggtitle(expression(atop(paste("Estimated versus Expected ",italic("HER2")," Copy Number of Validation Samples"),atop("pearson correlation:  0.9975")))) +theme(axis.text=element_text(size=16),axis.title=element_text(size=12,face="bold"),plot.title = element_text(lineheight=.8, face="bold")) + xlim(0,35) + ylim(0,35)
dev.off()