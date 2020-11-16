library(ggplot2)

setwd('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/ampCov/good_samples')
good_samples = list.files(pattern='*.txt',full.names = T)

#print(run_files)
amp_good = c()

for ( i in 1:length(good_samples)){
  
  print(good_samples[i])
  tt <- read.table(good_samples[i],header=F)
  amp_good = c(amp_good, tt$V3)
}

df_good = data.frame(amp_good)
mean(df_good$amp_good)
median(df_good$amp_good)

df_good_fail = subset(df_good, amp_good >= 10)

ggplot(df_good, aes(x=amp_good)) + 
  geom_freqpoly() +
  geom_vline(xintercept = 5, color = "red") +
  geom_vline(xintercept = 7.5, color = "blue") +
  geom_vline(xintercept = 10, color = "black") +
  labs(x = "Fraction Percentage of Amplicons < 400X") +
  ggtitle("Good Quality Samples")


setwd('/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/ampCov/bad_samples/')
bad_samples = list.files(pattern='*.txt',full.names = T)

amp_bad = c()

for ( i in 1:length(bad_samples)){
  
  print(bad_samples[i])
  tt <- read.table(bad_samples[i],header=F)
  amp_bad = c(amp_bad, tt$V3)
}

df_bad = data.frame(amp_bad)
mean(df_bad$amp_bad)
median(df_bad$amp_bad)

ggplot(df_bad, aes(x=amp_bad)) + 
  geom_freqpoly() +
  geom_vline(xintercept = 5, color = "red") +
  labs(x = "Fraction Percentage of Amplicons < 400X") +
  ggtitle("Poor Quality Samples")
