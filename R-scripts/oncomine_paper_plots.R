library(ggplot2)
library(openxlsx)
library(grid)
library(weights)

setwd("/Users/sir2013/Documents/oncomine/analysis/Paper/excel-sheets")

###BRAF###
braf = read.xlsx("BRAF.xlsx")

braf_cor = sub("^(-?)0.", "\\1.", sprintf("%.2f",cor(braf$`CGMP_50_VAF.(%)`,braf$`OnCORseq_VAF.(%)`,method="pearson")))
braf_title_tmp = paste("A.")
braf_title = paste(braf_title_tmp)

grob = grobTree(textGrob(label=paste0("p = ",braf_cor), x=0.01,  y=0.95, hjust=0, gp=gpar(col="black", fontsize=20, fontface = 'italic')))

ggplot(braf, aes(x = braf$`CGMP_50_VAF.(%)`, y = braf$`OnCORseq_VAF.(%)`)) +
  geom_point(aes(colour = braf$p_mutation),size = 4) +
  labs(x = "AmpliSeq VAF %", y = "Oncomine VAF %") +
  ggtitle(braf_title) + xlim(0,40) + ylim(0,40) + theme_bw() + theme(text = element_text(size=20)) +
  geom_abline(intercept=0, slope=1) + scale_colour_discrete(name="Mutation") +
  annotation_custom(grob) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-3/BRAF_vaf.pdf", plot = last_plot())


###EGFR###
egfr = read.xlsx("EGFR.xlsx")

egfr_cor = sub("^(-?)0.", "\\1.", sprintf("%3.2f",cor(egfr$`CGMP_50_VAF.(%)`,egfr$`OnCORseq_VAF.(%)`,method="pearson")))
egfr_title_tmp = paste("B.")
egfr_title = paste(egfr_title_tmp)

grob = grobTree(textGrob(label=paste0("p = ",egfr_cor), x=0.01,  y=0.95, hjust=0, gp=gpar(col="black", fontsize=20, fontface = 'italic')))

ggplot(egfr, aes(x = egfr$`CGMP_50_VAF.(%)`, y = egfr$`OnCORseq_VAF.(%)`)) +
  geom_point(aes(colour = egfr$p_mutation),size = 4) +
  labs(x = "AmpliSeq VAF %", y = "Oncomine VAF %") +
  ggtitle(egfr_title) + xlim(0,80) + ylim(0,80) + theme_bw() + theme(text = element_text(size=20)) +
  geom_abline(intercept=0, slope=1) + scale_colour_discrete(name="Mutation") +
  annotation_custom(grob) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-3/EGFR_vaf.pdf", plot = last_plot())


###IDH1###
idh1 = read.xlsx("IDH1.xlsx")

idh1_cor = sub("^(-?)0.", "\\1.", sprintf("%3.2f",cor(idh1$`CGMP_50_VAF.(%)`,idh1$`OnCORseq_VAF.(%)`,method="pearson")))
idh1_title_tmp = paste("C.")
idh1_title = paste(idh1_title_tmp)

grob = grobTree(textGrob(label=paste0("p = ",idh1_cor), x=0.01,  y=0.95, hjust=0, gp=gpar(col="black", fontsize=20, fontface = 'italic')))

ggplot(idh1, aes(x = idh1$`CGMP_50_VAF.(%)`, y = idh1$`OnCORseq_VAF.(%)`)) +
  geom_point(aes(colour = idh1$p_mutation),size = 4) +
  labs(x = "AmpliSeq VAF %", y = "Oncomine VAF %") +
  ggtitle(idh1_title) + xlim(0,70) + ylim(0,70) + theme_bw() + theme(text = element_text(size=20)) +
  geom_abline(intercept=0, slope=1) + scale_colour_discrete(name="Mutation") +
  annotation_custom(grob) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-3/IDH1_vaf.pdf", plot = last_plot())

###KRAS###
kras = read.xlsx("KRAS.xlsx")

kras_cor = sub("^(-?)0.", "\\1.", sprintf("%3.2f",cor(kras$`CGMP_50_VAF.(%)`,kras$`OnCORseq_VAF.(%)`,method="pearson")))
kras_title_tmp = paste("D.")
kras_title = paste(kras_title_tmp)

grob = grobTree(textGrob(label=paste0("p = ",kras_cor), x=0.01,  y=0.95, hjust=0, gp=gpar(col="black", fontsize=20, fontface = 'italic')))

ggplot(kras, aes(x = kras$`CGMP_50_VAF.(%)`, y = kras$`OnCORseq_VAF.(%)`)) +
  geom_point(aes(colour = kras$p_mutation),size = 4) +
  labs(x = "AmpliSeq VAF %", y = "Oncomine VAF %") +
  ggtitle(kras_title) + xlim(0,70) + ylim(0,70) + theme_bw() + theme(text = element_text(size=20)) +
  geom_abline(intercept=0, slope=1) + scale_colour_discrete(name="Mutation") +
  annotation_custom(grob) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-3/KRAS_vaf.pdf", plot = last_plot())


###NRAS###
nras = read.xlsx("NRAS.xlsx")

nras_cor = sub("^(-?)0.", "\\1.", sprintf("%3.4f",cor(nras$`CGMP_50_VAF.(%)`,nras$`OnCORseq_VAF.(%)`,method="pearson")))
nras_title_tmp = paste("E.")
nras_title = paste(nras_title_tmp)

grob = grobTree(textGrob(label=paste0("p = ",kras_cor), x=0.01,  y=0.95, hjust=0, gp=gpar(col="black", fontsize=20, fontface = 'italic')))

ggplot(nras, aes(x = nras$`CGMP_50_VAF.(%)`, y = nras$`OnCORseq_VAF.(%)`)) +
  geom_point(aes(colour = nras$p_mutation),size = 4) +
  labs(x = "AmpliSeq VAF %", y = "Oncomine VAF %") +
  ggtitle(nras_title) + xlim(0,70) + ylim(0,70) + theme_bw() + theme(text = element_text(size=20)) +
  geom_abline(intercept=0, slope=1) + scale_colour_discrete(name="Mutation") +
  annotation_custom(grob) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-3/NRAS_vaf.pdf", plot = last_plot())


###PIKC3A###
pik3ca = read.xlsx("PIK3CA.xlsx")

pik3ca_cor = sub("^(-?)0.", "\\1.", sprintf("%3.2f",cor(pik3ca$`CGMP_50_VAF.(%)`,pik3ca$`OnCORseq_VAF.(%)`,method="pearson")))
pik3ca_title_tmp = paste("F.")
pik3ca_title = paste(pik3ca_title_tmp)

grob = grobTree(textGrob(label=paste0("p = ",pik3ca_cor), x=0.01,  y=0.95, hjust=0, gp=gpar(col="black", fontsize=20, fontface = 'italic')))

ggplot(pik3ca, aes(x = pik3ca$`CGMP_50_VAF.(%)`, y = pik3ca$`OnCORseq_VAF.(%)`)) +
  geom_point(aes(colour = pik3ca$p_mutation),size = 4) +
  labs(x = "AmpliSeq VAF %", y = "Oncomine VAF %") +
  ggtitle(pik3ca_title) + xlim(0,50) + ylim(0,50) + theme_bw() + theme(text = element_text(size=20)) +
  geom_abline(intercept=0, slope=1) + scale_colour_discrete(name="Mutation") +
  annotation_custom(grob) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-3/PIK3CA_vaf.pdf", plot = last_plot())


##########Mixtures##########

###M1###

m1 = read.xlsx("M1.xlsx")

ggplot(m1, aes(x = factor(m1$Mutation))) + 
  geom_point(aes(y = m1$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m1$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m1$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 1") + ylim(0,15) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M1.pdf", plot = last_plot())


###M2###

m2 = read.xlsx("M2.xlsx")

ggplot(m2, aes(x = factor(m2$Mutation))) + 
  geom_point(aes(y = m2$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m2$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m2$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 2") + ylim(0,15) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M2.pdf", plot = last_plot())


###M3###

m3 = read.xlsx("M3.xlsx")

ggplot(m3, aes(x = factor(m3$Mutation))) + 
  geom_point(aes(y = m3$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m3$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m3$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 3") + ylim(0,15) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M3.pdf", plot = last_plot())

###M4###

m4 = read.xlsx("M4.xlsx")

ggplot(m4, aes(x = factor(m4$Mutation))) + 
  geom_point(aes(y = m4$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m4$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m4$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 4") + ylim(0,25) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M4.pdf", plot = last_plot())

###M5###

m5 = read.xlsx("M5.xlsx")

ggplot(m5, aes(x = factor(m5$Mutation))) + 
  geom_point(aes(y = m5$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m5$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m5$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 5") + ylim(0,30) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M5.pdf", plot = last_plot())

###M6###

m6 = read.xlsx("M6.xlsx")

ggplot(m6, aes(x = factor(m6$Mutation))) + 
  geom_point(aes(y = m6$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m6$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m6$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 6") + ylim(0,20) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M6.pdf", plot = last_plot())

###M7###

m7 = read.xlsx("M7.xlsx")

ggplot(m7, aes(x = factor(m7$Mutation))) + 
  geom_point(aes(y = m7$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m7$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m7$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 7 Triplicate across three Runs") + ylim(0,30) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M7.pdf", plot = last_plot())

###M8###

m8 = read.xlsx("M8.xlsx")

ggplot(m8, aes(x = factor(m8$Mutation))) + 
  geom_point(aes(y = m8$R1.VAF, shape = "Run1", color = "Run1"), size = 4) + 
  geom_point(aes(y = m8$R2.VAF, shape = "Run2", color = "Run2"), size = 4) +
  geom_point(aes(y = m8$R3.VAF, shape = "Run3", color = "Run3"), size = 4) +
  labs(x = "Mutation", y = "VAF %") +
  ggtitle("Mixture 8") + ylim(0,15) + theme_bw() + 
  theme(axis.text.x = element_text(angle = 45, size = 18, hjust = 1),text = element_text(size=20)) +
  scale_shape_manual(name = "RUNS", values=c(Run1=15, Run2=16, Run3=17))+ 
  scale_color_manual(name = "RUNS", values=c(Run1="red", Run2="blue", Run3="black")) +
  ggsave(filename = "/Users/sir2013/Documents/oncomine/analysis/Paper/plots/table-5/M8.pdf", plot = last_plot())
