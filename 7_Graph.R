# Libraries
#install.packages('ggplot2',repos='https://pbil.univ-lyon1.fr/CRAN/')
#install.packages('dplyr',repos='https://pbil.univ-lyon1.fr/CRAN/')
#install.packages('forcats',repos='https://pbil.univ-lyon1.fr/CRAN/')
library(ggplot2)
library(dplyr)
library(forcats)

require(data.table)

Sys.setlocale("LC_ALL", "en_GB.UTF-8")
sessionInfo()
#############
#
#  Benefit.tsv
#  'DOI' \t 'Created date' \t ' Nb Undue Citations'
#############
data<-read.table(file = 'data/method1_benefit.tsv', sep = '\t', header = TRUE)
colnames(data)
data$created.Date<-as.Date(as.POSIXct(data$created.Date, tz = "UTC", format = "%Y-%m-%dT%H:%M:%OSZ"))
#
# Creation date of benefiter
p<-ggplot(data, aes(x=created.Date, y=Nb.Undue.Citations))+scale_x_date(date_labels = "%m-%Y")+geom_point(shape=18, fill="blue", color="darkred", size=3)+xlab("Date when the paper benefiting from sneaked references was created with Crossref")+ylab("Total number of undue citations benefiting to the registered paper (min 1)")
pdf("Fig/UndueVSTime.pdf")
p
dev.off()
# Zoom after march 2024 before dec. 2024
p<-ggplot(data, aes(x=created.Date, y=Nb.Undue.Citations))+scale_x_date(date_labels = "%m-%Y")+geom_point(shape=18, fill="blue", color="darkred", size=3)+xlab("Date (2024) when a paper benefiting from sneaked references was created with Crossref")+ylab("Total number of undue citations benefiting to the registered paper (min 1)")+xlim(as.Date("01/03/2024","%d/%m/%Y"),as.Date("01/12/2024","%d/%m/%Y"))
pdf("Fig/UndueVSTimeZoom.pdf")
p
dev.off()

# The ones that benefit the most
data2 <- mutate(data, DOI = fct_reorder(DOI, Nb.Undue.Citations))
p <- ggplot(data2[0:30,], aes(x=DOI,y=Nb.Undue.Citations)) +
geom_bar(stat="identity", fill="#f68060", alpha=.6, width=.4) + coord_flip() +
xlab("") + theme_bw() + geom_text(aes(label=Nb.Undue.Citations), position=position_dodge(width=0.9), hjust=-0.15) + ylim(0,6400)
pdf("Fig/BenfBarChart.pdf")
p
dev.off()
# Bar plot of undue citation per sigle paper
p <- ggplot(data2, aes(x=Nb.Undue.Citations)) + xlab("Number of Undue citations (per single paper)")+ylab("Amount of papers with x undue citations")+geom_histogram(color="darkblue", fill="lightblue")
pdf("Fig/BenfBarAll.pdf")
p
dev.off()
# Zoom
dd <- data2[data2$Nb.Undue.Citations>1,]
p <- ggplot(dd, aes(x=Nb.Undue.Citations)) + xlab("Number of Undue citation (per single benefiting paper)")+ylab("Amount of papers with x undue citations")+geom_histogram(color="darkblue", fill="lightblue")#+xlim(1,6000)
pdf("Fig/BenfBarAllZoom.pdf")
p
dev.off()

# Stat benefiter
nrow(data2)
# 2703
# Sum... Total number of Sneaked ref.
sum(data2$Nb.Undue.Citations)
# 80821
summary(data2$Nb.Undue.Citations)
#Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
#
1.0     1.0     1.0    29.9     1.0  6059.0
# Nb of benefiter of a single citation=
dd <- data2[data2$Nb.Undue.Citations==1,]
nrow(dd)
# 2469
dd <- data2[data2$Nb.Undue.Citations<30,]
nrow(dd)
dd <- data2[data2$Nb.Undue.Citations<31,]
nrow(dd)
dd <- data2[data2$Nb.Undue.Citations<30 & data2$Nb.Undue.Citations>1,]
nrow(dd)



#############
#
#  Compare.tsv
#  DOI      created Date      deposited      Crossref ReferencesNbr      XML ReferencesNbr      Diff      Nb Sneaked      Nb Sneaked List      Nb Other After Last      Other After Last List      Raw Last      State
#############

data3<-read.table(file = 'data/results_method1.tsv', skip=2, sep = '\t', header = TRUE)
colnames(data3)
# Total number of sneaked:
sum(data3$Nb.Sneaked)
#80821

# Grobid non empty list
dg <- data3[data3$XML.ReferencesNbr!=0,]
nrow(dg)
#3940
# Grobid non empty list and Crosref non empty
dg <- dg[dg$Crossref.ReferencesNbr!=0,]
nrow(dg)
#3132
# Total number of sneaked when both list not empty:
sum(dg$Nb.Sneaked)
# 78736

# Case1:
Case1 <- dg[dg$Nb.Sneaked==0 & dg$Nb.Other.After.Last==0 & dg$State=='After_Last',]
nrow(Case1)
# 331
# Case2:
# Good ones (Sneaked found and no false positive (Other.After.Last)
Case2_OK <- dg[(dg$Nb.Sneaked>0 & dg$Nb.Other.After.Last==0) & dg$State=='After_Last',]
nrow(Case2_OK)
# 1788
sum(Case2_OK$Nb.Sneaked)
# 46297
# False positive: No Sneaked but (Other.After.Last) not zero
nrow(dg[(dg$Nb.Sneaked==0 & dg$Nb.Other.After.Last>0) & dg$State=='After_Last',])
# 22
# False positive: Sneaked but (Other.After.Last) not zero
nrow(dg[(dg$Nb.Sneaked>0 & dg$Nb.Other.After.Last>0) & dg$State=='After_Last',])
# 818
Case2_KO <- dg[dg$Nb.Other.After.Last>0 & dg$State=='After_Last',]
nrow(Case2_KO)
# 840
sum(Case2_KO$Nb.Other.After.Last)
# 2032
# Case 3
Case3 <- dg[dg$State=='AF_L',]
nrow(Case3)
# 173
sum(Case3$Nb.Sneaked)
# 3176

### Comparing raw number Grobid / Xref
sum(dg[dg$Diff>0,]$Diff)
# 84270

###################
#
# Time
#
###################
data3$created.Date<-as.Date(as.POSIXct(data3$created.Date, tz = "UTC", format = "%Y-%m-%dT%H:%M:%OSZ"))
data3$deposit<-as.Date(as.POSIXct(data3$deposit, tz = "UTC", format = "%Y-%m-%dT%H:%M:%OSZ"))
data3$Date.Difference. <- data3$deposit - data3$created.Date

pdf("Fig/SneakedVSTime.pdf")
p<-ggplot(data3, aes(x=created.Date, y=Nb.Sneaked))+scale_x_date(date_labels = "%m-%Y")+geom_point(shape=18)+ xlab("Date when a paper was registered")+ylab("Number of references sneaked in at registration time (min 0)")
p
dev.off()

#Sneaked Stats
# Nb of lines:
nrow(data3)
# 4111
# Nb of lines with Sneaked:
Papers.With.S <- data3[data3$Nb.Sneaked>0,]
nrow(Papers.With.S)
# 2818
# Nb of lines where Crossref.ReferencesNbr is not zero
Papers.With.Xref <- data3[data3$Crossref.ReferencesNbr>0,]
nrow(Papers.With.Xref)
# 3250
# Nb of lines where XML is not zero
Papers.With.XML <- data3[data3$XML.ReferencesNbr>0,]
nrow(Papers.With.XML)
# Sum... Total number of Sneaked ref.
sum(data3$Nb.Sneaked)
# Stat Summary of sneaked ref
summary(data3$Nb.Sneaked)
summary(Papers.With.S$Nb.Sneaked)
Papers.With <- Papers.With.S[Papers.With.S$Nb.Sneaked==4,]
nrow(Papers.With)

Papers.With.S<-data3[data3$Nb.Sneaked>0,]
pdf("Fig/SneakedVSTime.pdf")
p<-ggplot(Papers.With.S, aes(x=created.Date, y=Nb.Sneaked))+scale_x_date(date_labels = "%m-%Y")+geom_point(shape=18)+ xlab("Date when a paper with sneaked ref. was registered")+ylab("Number of references sneaked in at registration time (min 1)")
p
dev.off()

pdf("Fig/SneakedPerPaperBar.pdf")
p <- ggplot(data3, aes(x=Nb.Sneaked)) + xlab("Number of sneaked ref (in single paper)")+ylab("Amount of papers where x references were sneaked in")+geom_histogram(color="darkblue", fill="lightblue")#+xlim(-1,28)
p
dev.off()
pdf("Fig/SneakedPerPaperBarZoom.pdf")
p <- ggplot(Papers.With.S, aes(x=Nb.Sneaked)) + xlab("Number of sneaked ref (in single paper)")+ylab("Amount of papers where x references were sneaked in")+geom_histogram(color="darkblue", fill="lightblue")#+xlim(-1,28)
p
dev.off()

data_sub = data[data$Nb.Undue.Citations !=0,]
data_sub3 = data3[data3$Nb.Sneaked !=0,]
#data_sub = data
#data_sub3 = data3
pdf("Fig/UnSnVSTime.pdf")
p <- ggplot(data_sub, aes(x=created.Date, y=Nb.Undue.Citations))+geom_point(shape=18, color="blue", size=3)+geom_point(data=data_sub3, aes(x=created.Date, y=Nb.Sneaked), color="red", size=2)+xlim(as.Date("01/03/2024","%d/%m/%Y"),as.Date("01/12/2024","%d/%m/%Y"))
p
dev.off()


#+scale_x_date(date_labels = "%m-%Y")+scale_y_date(date_labels = "%m-%Y")+geom_point(color="blue", size=3)
#data3<-read.table(file = 'Compare.tsv', skip=2, sep = '\t', header = TRUE)
#colnames(data3)

#Ndata3<-data3[data3$Nb.Sneaked>0,]
pdf("Fig/DateSneakedTrans.pdf")
p<-ggplot(Papers.With.S, aes(x=created.Date, y=Nb.Sneaked))+geom_point(color="blue", size=3,alpha = 0.05)+ xlab("Creation date")+ylab("Number of sneaked references")
p
dev.off()

pdf("Fig/CrossRefBar.pdf")
p <- ggplot(data3, aes(x=Crossref.ReferencesNbr)) + xlab("Number of ref according to CrosRef (in a single paper)")+ylab("Amount of papers whith x references")+geom_histogram(color="darkblue", fill="lightblue")
p
dev.off()

pdf("Fig/GroXMLBar.pdf")
p <- ggplot(data3, aes(x=XML.ReferencesNbr)) + xlab("Number of ref according to Grobid/XML (in a single paper)")+ylab("Amount of papers whith x references")+geom_histogram(color="darkblue", fill="lightblue")
p
dev.off()

pdf("Fig/DiffBar.pdf")
p <- ggplot(data3, aes(x=Diff)) + xlab("Diff between CrossRef and Grobid/XML")+ylab("Amount of papers whith x references")+geom_histogram(color="darkblue", fill="lightblue")
p
dev.off()



data4<-read.table(file = 'data/method1_time.tsv', sep = '\t', header = TRUE)
colnames(data4)
data4$Date.from..Citing.Paper.<-as.Date(as.POSIXct(data4$Date.from..Citing.Paper., tz = "UTC", format = "%Y-%m-%dT%H:%M:%OSZ"))
data4$Date.To..Cited.Paper.<-as.Date(as.POSIXct(data4$Date.To..Cited.Paper., tz = "UTC", format = "%Y-%m-%dT%H:%M:%OSZ"))
data4$Date.Difference. <- data4$Date.from..Citing.Paper. - data4$Date.To..Cited.Paper.
#color <- c("blue","red")[1+ (data4$Date.from..Citing.Paper. == data4$Date.To..Cited.Paper.)]
summary(as.numeric(data4$Date.Difference.))
#   Min. 1st Qu.  Median    Mean 3rd Qu.    Max.    NA's
#    0.0    16.0    33.0    38.3    55.0  1295.0     312

pdf("Fig/Coherence.pdf")
p <- ggplot(data4, aes(x=Date.from..Citing.Paper., y=Date.Difference.))+geom_point(color="blue", size=3,alpha = 0.1)+ xlab("Creation date of a citing DOI")+ylab("Time Difference, citing creation date minus cited creation date")
p
dev.off()

pdf("Fig/CoherenceZoom.pdf")
p <- ggplot(data4, aes(x=Date.from..Citing.Paper., y=Date.Difference.))+ylim(0,250)+geom_point(color="blue", size=3,alpha = 0.1)+ xlab("Creation date of a citing DOI")+ylab("Time Difference, citing creation date minus cited creation date")
p
dev.off()


pdf("Fig/TimeDiffBar.pdf")
NoNA <- data4[!is.na(data4$Date.Difference.),]
days.diff <- as.numeric(NoNA$Date.Difference.)
ggplot()+aes(days.diff)+geom_histogram(color="darkblue", fill="lightblue", bins = 101)+xlim(0,100)
dev.off()

#ggplot(data3, aes(x=Diff)) +
#    geom_histogram(aes(y=..density..),      # Histogram with density instead of count on y-axis
#                   colour="black", fill="white") +
#    geom_density(alpha=.2, fill="#FF6666")
#ggplot(data3, aes(x=XML.ReferencesNbr)) +
#    geom_histogram(aes(y=..density..),      # Histogram with density instead of count on y-axis
#                   colour="black", fill="white") +
#    geom_density(alpha=.2, fill="#FF6666")
#ggplot(data3, aes(x=Crossref.ReferencesNbr)) +
#    geom_histogram(aes(y=..density..),      # Histogram with density instead of count on y-axis
#                   colour="black", fill="white") +
#    geom_density(alpha=.2, fill="#FF6666")
