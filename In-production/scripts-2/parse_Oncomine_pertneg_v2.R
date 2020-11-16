options(stringsAsFactors = FALSE)
library(data.table)
#Function for range of positions used later
`%between%` <- function(x,y) between(x,y[1],y[2],incbounds=TRUE)
#Disabled filtering via IonReporter VCF calls...
parse_Pert_Neg <- function(vcf, TargetSheet){
  #Read in mpileup vcf and known variants vcf 
  test <- read.table(vcf)
  #Pull columns and split condensed columns
  ConvertVcf <- function(test){
    Chrom <- sub(pattern = 'chr',replacement = '',x=test$V1)
    Pos <- as.character(test$V2)
    Ref <- as.character(test$V4)
    Alt <- as.character(test$V5)
    Info <- as.character(test$V8)
    Info2 <- strsplit(Info,split=';')
    DP <- c()
    #The new bcftools (1.2.1) call outputs the DP4= format
    DP4 <- c()
    for (i in 1:length(Info2)){
      if (grepl('^INDEL',Info2[[i]])){
        DP[i] <- sub(pattern='DP=',replacement='',x=Info2[[i]][grepl('^DP=',Info2[[i]])])
        DP4[i] <- sub(pattern='DP4=',replacement='',x=Info2[[i]][grepl('^DP4=',Info2[[i]])])
      } else{
        DP[i] <- sub(pattern='DP=',replacement='',x=Info2[[i]][grepl('^DP=',Info2[[i]])])
        DP4[i] <- sub(pattern='DP4=',replacement='',x=Info2[[i]][grepl('^DP4=',Info2[[i]])])
      }
    }
    DP4_2 <- strsplit(DP4,split=',')
    FR <- c()
    RR <- c()
    FNR <- c()
    RNR <- c()
    for (i in 1:length(DP4_2)){
      FR[i] <- DP4_2[[i]][1]
      RR[i] <- DP4_2[[i]][2]
      FNR[i] <- DP4_2[[i]][3]
      RNR[i] <- DP4_2[[i]][4]
    }
    #temp data frame 
    outdf <- data.frame(Chrom,Pos,Ref,Alt,DP,FR,RR,FNR,RNR)
    return(outdf)
  }
  outdf <- ConvertVcf(test = test)
  #Add a function to parse the spreadsheet of pertinent negative targets -- modular to a changing target list
  ParseTargets <- function(TargetSheet){
    TarSheet <- read.csv(TargetSheet,header=T)
    Target <- as.character(TarSheet$Genomic.region..hg19.b37..coordinates..mostly.applicable.to.CLIA.alterations.)
    Gene <- as.character(TarSheet$GENE)
    Alterations <- as.character(TarSheet$Alterations)
    Gene.Target <- paste(Gene,Alterations,sep=' ')
    #Parse apart the positional info
    Chrom <- c()
    Start <- c()
    End <- c()
    cc <- strsplit(Target,split = ':')
    Pos <- c()
    for (i in 1:length(cc)){
      Chrom[i] <-  cc[[i]][1]
      Pos[i] <- cc[[i]][2]
    }
    dd <- strsplit(Pos,split='-')
    for (j in 1:length(dd)){
      Start[j] <- dd[[j]][1]
      End[j] <- dd[[j]][2]
    }
    #Now bind them into a df
    TargettedFrame <- data.frame(Gene.Target,Chrom,Start,End)
    return(TargettedFrame)
  }
  TargettedFrame <- ParseTargets(TargetSheet = TargetSheet)
  
  #Per Gene Target Data frames -- gotta fix this based upon ParseTargets Results
  CalculateTargets <- function(outdf, TargettedFrame){
    BBlist <- list()
    #Loop through TargettedFrame
    for (i in 1:length(TargettedFrame$Gene.Target)){
      Match1 <- data.frame(outdf[as.numeric(as.character(outdf$Chrom)) == as.numeric(as.character(TargettedFrame$Chrom[i])) & as.numeric(as.character(outdf$Pos)) %between% c(as.numeric(as.character(TargettedFrame$Start[i])),as.numeric(as.character(TargettedFrame$End[i]))),])
      BBlist[[i]] <- Match1
    }
    #Now we should annotate the entries as needed
    GeneTargets <- unique(as.character(TargettedFrame$Gene.Target))
    for (j in 1:length(BBlist)){
      if (length(BBlist[[j]]$Chrom) > 0){
        BBlist[[j]]$Gene.Target <- GeneTargets[j]
      }
    }
    BBdf1 <- do.call(rbind,BBlist)
    #print(BBdf1)
    write.csv(BBdf1, file = "BBdf1.csv")
    return(BBdf1)
  }
  BBdf <- CalculateTargets(outdf = outdf,TargettedFrame = TargettedFrame)
  PertNegTargets <- unique(BBdf$Gene.Target)
  
  #Aggregate averages of all targets, sort and report by variant call depths ?
  BBdf[,5] <- as.numeric(as.character(BBdf[,5]))
  BBdf[,6] <- as.numeric(as.character(BBdf[,6]))
  BBdf[,7] <- as.numeric(as.character(BBdf[,7]))
  BBdf[,8] <- as.numeric(as.character(BBdf[,8]))
  BBdf[,9] <- as.numeric(as.character(BBdf[,9]))
  Nonref <- as.numeric(as.character(BBdf$FNR)) + as.numeric(as.character(BBdf$RNR))
  BBdf$Nonref <- Nonref
  
  #Now just filter on PertNegTargets and return the sorted data frame!
  PertNegDf <- BBdf[BBdf$Gene.Target %in% PertNegTargets,]
  PND <- PertNegDf[order(PertNegDf$Nonref,decreasing = T),]
  
  ######Now we should add something to reformat these as similar to rest of variant tabs as possible:
  VarHeader <- c('Patient Name','Accession #','Sample ID','DNA Barcode','RNA Barcode','Surgical Path #','Tumor','Tissue','Block','Cellularity','Sample Avg. Coverage','Mutation','Type','Oncomine Gene Class','Tier','Frequency','Quality','COSMIC ID','Total Coverage','Exon','Strand Bias','Exclude','Warnings','Interpretation','Citations','ExAC_AF','1000G_AF','clinvar_rs')
  #Useful variable to fill in blank columns where annotation is missing:
  BlankColumn <- rep('',times=length(PND$Nonref))
  #Mutations Requires some parsing to get it into the correct format...
  Mutations <- c()
  for (i in 1:length(PND$Gene.Target)){
    Mutations[i] <- paste(paste(strsplit(PND$Gene.Target[i],split=' ')[[1]][1],paste('Chr',PND$Chrom[i],':',PND$Pos[i],sep = ''),paste(PND$Ref[i],'>',strsplit(PND$Alt[i],split=',')[[1]][1],sep=''),sep=' '),strsplit(PND$Gene.Target[i],split=' ')[[1]][2],sep=',') 
  }
  sname <- (strsplit(basename(vcf),split='\\.')[[1]][1])
  dDF <- data.frame(BlankColumn,BlankColumn,rep(strsplit(sname,split = '_')[[1]][1],times=length(PND$Nonref)),BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,(Mutations),(BlankColumn),BlankColumn,BlankColumn,paste(round(x=((PND$Nonref/PND$DP)*100),digits=2),'%',sep=''),BlankColumn,BlankColumn,(PND$DP),(BlankColumn),BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn,BlankColumn)
  colnames(dDF) <- VarHeader
  dDF2 <- dDF[order(as.numeric(gsub(x=dDF$Frequency,pattern = '%',replacement = '')),decreasing = T),]
  rez <- dDF2
  return(rez)
}

args = commandArgs(trailingOnly=TRUE)
mpileupvcf <- args[1]
TargetSheet <- args[2]
SampleName <- basename(mpileupvcf)
OutputName <- paste('./',SampleName,'.PertinentNegatives.xls',sep='')
Results <- parse_Pert_Neg(mpileupvcf,TargetSheet)
write.table(Results,file=OutputName,row.names = F,quote=F,sep='\t')
