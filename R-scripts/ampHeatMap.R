library(ggplot2)
library(pheatmap)

setwd("/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/ampCov/good_samples")
samples = Sys.glob("RUN*/O*/OCP*/qc/StatsActor/amplicons*")
#print(samples[1])

tt <- read.table(samples[1],header=F)
ampID = data.frame(tt$V2)
ampID[2] = tt$V3
ampID[3] = tt$V4

df = data.frame(tt$V12)
colnames(df)[1] <- "V1"

print(length(samples))

for ( i in 2:length(samples)){
  tt <- read.table(samples[i],header=F)
  df[i] = tt$V12
}

#df$mean = apply(df,1,mean)
#df$min = apply(df,1,min)
#df$max = apply(df,1,max)

dm = data.matrix(df)

for(i in 1:2530){
  for(j in 1:108){
    if(dm[i,j] < 400){
      dm[i,j] = 1
    }
    else{
      dm[i,j] = 0
    }
  }
}

count = 0

for(i in 1:length(dm_rowSum)){
  if(dm_rowSum[i] > 10 ){
    count = count +1
  }
}

dm_rowSum = rowSums(dm)
dm_rowSum = data.frame(dm_rowSum)

dm_rowSum$min = apply(df,1,min)
dm_rowSum$max = apply(df,1,max)
dm_rowSum$avg = apply(df,1,mean)

ampID[4] = dm_rowSum$dm_rowSum
ampID[5] = dm_rowSum$min
ampID[6] = dm_rowSum$max
ampID[7] = dm_rowSum$avg

fail_amp = subset(ampID, ampID$V4 == 108)
write.table(fail_amp, "/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/ampCov/good_samples/recurring_failAmps.txt", sep="\t")

pheatmap(dm, cluster_cols = FALSE, cluster_rows = FALSE, main = "Amplicon Coverage")
