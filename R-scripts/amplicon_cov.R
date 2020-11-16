setwd("/Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/Run35-amplicons/")

amp = read.table("IonXpress_001_R_2017_05_09_08_11_18_user_S5XL-00489-92-OCP_RUN35_CHIP1_Auto_user_S5XL-00489-92-OCP_RUN35_CHIP1_157.amplicon.cov.xls", header = TRUE)

amp_subset = as.character(amp$contig_id)
amp_subset = cbind(amp_subset, amp$contig_srt)
amp_subset = cbind(amp_subset, amp$contig_end)
amp_subset = cbind(amp_subset, as.character(amp$region_id))
amp_subset = cbind(amp_subset, as.character(amp$attributes))

filename = system("ls /Users/sir2013/Documents/Weill_Cornell/ipm/oncomine/Run35-amplicons/",intern=TRUE)

for(i in 1:length(filename)){
  
  file = read.table(filename[i],header=TRUE) ## if you have headers in your files ##
  amp_subset = cbind(amp_subset, file$total_reads)
  
  #write.table(mean,file=paste("/dir",paste("mean",filename[i],sep="."),sep="/")) 
  ##if you wish to write the means of all the files in seperate files rather than one.
}

amp_df = as.data.frame(amp_subset, stringsAsFactors=FALSE)

for (column in 6:24) {
  amp_df[, column] <- as.numeric(amp_df[, column])
}

total_reads = rowSums(amp_df[,c(6:24)])
#summed <- rowSums(zscore[, c(1, 2, 3, 5)])
avg = (total_reads / 19)
amp_df = cbind(amp_df, total_reads)
amp_df = cbind(amp_df, avg)
