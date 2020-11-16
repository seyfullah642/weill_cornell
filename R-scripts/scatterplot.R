library(openxlsx)

onco = read.xlsx("Oncomine_EXaCT-1_VAF-DP.xlsx")
onco_subset = read.xlsx("Oncomine_EXaCT-1_VAF-DP_subset.xlsx")

plot(onco$oncomine.vaf,onco$exact1.vaf,xlab="Oncomine VAF",ylab="EXaCT-1 VAF")
abline(h=0.1, v=0.05, col = "gray60")

plot(onco_subset$oncomine.vaf,onco_subset$exact1.vaf,xlab="Oncomine VAF",ylab="EXaCT-1 VAF")
#plot.xlim(0,1)
#plot.ylim(0,1)
abline(h=0.1, v=0.05, col = "gray60")

#onco = read.table("Oncomine.txt", header=TRUE)
#wes = read.csv("EXaCT-1_VAF.csv", header=F);colnames(wes)=c("SampleID", "chrom", "start", "end", "ref", "alt", "mut.tumor.depth", "tumor.depth", "mut.normal.depth", "normal.depth", "vaf")

#onco$ID = sprintf("%s_%s", gsub("chr", "", onco$chrom), onco$start)
#wes$ID = sprintf("%s_%s", wes$chrom, wes$start)
##wes = droplevels( wes[ wes$ID != "NA_NA", ])

##final = unique(merge( onco, wes, by="ID"))
#final = merge( onco, wes, by="ID")
#plot.df = unique(final[ , c("vaf.x", "vaf.y")])
#plot( plot.df)

