library(ggplot2)
library(xlsx)

setwd("/Users/sir2013/Documents/Weill_Cornell/ipm/training/geneCov")

hiseq2500 = read.table("HiSeq2500_summary.stats.txt", header=TRUE, sep="\t")
hiseq4000 = read.table("HiSeq4000_summary.stats.txt", header=TRUE, sep="\t")

bedfiles = system("ls /Users/sir2013/Documents/Weill_Cornell/ipm/training/geneCov/*.cov.sorted.bed",intern=TRUE)

for(i in seq(1, 48, 2)){
  
  name = strsplit(basename(bedfiles[i+1]), "\\.")
  pdf_name = paste(name[[1]][1],".pdf",sep="")
  pdf(pdf_name)
  
  cov1 = read.table(bedfiles[i+1], header=FALSE, sep="\t", stringsAsFactors = FALSE, quote = "")
  cov2 = read.table(bedfiles[i], header=FALSE, sep="\t", stringsAsFactors = FALSE, quote = "")
  
  #print(name[[1]][1])
  
  #plot_name = paste(name[[1]][1],"_plot",sep="")
  
  mergedCov = merge(cov1,cov2,by=c("V2","V3"))
  
  ggplot(mergedCov, aes(x=V7.x, y= V7.y)) + 
    geom_point() +
    stat_smooth(method = "lm", col = "red") +
    xlab("HiSeq2500 read cov") +
    ylab("HiSeq4000 read cov") +
    ggtitle(name[[1]][1])
  
  dev.off()  
}


name = strsplit(basename(bedfiles[1]), "\\.")
name[[1]][1]
plot_name = paste(name[[1]][1],"_plot",sep="")
pdf("test.pdf")
cov2 = read.table("Sample_NA12878_060716_1_4000_Ctrl_HALO.cov.sorted.bed", header=FALSE, sep="\t", stringsAsFactors = FALSE, quote = "")
cov1 = read.table("Sample_NA12878_060716_1_Ctrl_HALO.cov.sorted.bed", header=FALSE, sep="\t", stringsAsFactors = FALSE, quote = "")

mergedCov = merge(cov1,cov2,by=c("V2","V3"))

#hiseq_stats_sorted = hiseq_stats[ sort.list(hiseq_stats$Total_num_of_reads.x, decreasing = F), ]
ggplot(mergedCov, aes(x=V7.x, y= V7.y)) +
  geom_point() +
  stat_smooth(method = "lm", col = "red") +
  xlab("HiSeq2500 read cov") +
  ylab("HiSeq4000 read cov") 
  #ggtitle("Test")
dev.off()
coef(lm(V7.x ~ V7.y, data = mergedCov))

ggplot(hiseq_stats, aes(x=Total_num_of_reads.x, y=Total_num_of_reads.y)) + 
  geom_point() +
  stat_smooth(method = "lm", col = "red")

coef(lm(Total_num_of_reads.x ~ Total_num_of_reads.y, data = hiseq_stats))
