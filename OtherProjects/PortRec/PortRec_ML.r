print("**********Execution started**********")


#Load packages
options(scipen=999)
options(warn=-1)
library(dplyr)
library(openxlsx)
library(kernlab)
library(e1071)

#Function for change datatype
changeDatatype <- function(object, datatype){
  if(datatype=='numeric'){
    return(as.numeric(object))
  }
  else if(datatype=='date'){
    if (class(object) == 'numeric') {
      return(as.Date(object, origin="1899-12-30"))
    }else if (class(object) == 'character') {
      object = as.numeric(object)
      return(as.Date(object, origin="1899-12-30"))
    }
    else {
      return(as.Date(object, format="%m/%d/%Y"))  
    }
    
  }
  else if(datatype=='dataframe'){
    return(as.data.frame(object))
  }
  else if(datatype=='factor'){
    return(as.factor(object))
  }
  else if(datatype=='vector'){
    return(as.vector(object))
  }
}

#Function to change column to factor
convertToFactor <- function(column, levels){
  return(factor(column, levels))
}

#Function to select column for dataframe
selectCol <- function(dataframe, collist){
  dataframe = dataframe[,which(names(dataframe) %in% collist)]
  return(dataframe)
}

#Function to delete columns from dataframe
deleteCol <- function(dataframe, collist){
  dataframe = dataframe[,-which(names(dataframe) %in% collist)]
  return(dataframe)
}

#Function for Imputing Break AGe and Curr.y with mode
Mode <- function (x, na.rm) {
  xtab <- table(x)
  xmode <- names(which(xtab == max(xtab)))
  if (length(xmode) > 1) xmode <- ">1 mode"
  return(xmode)
}

#Function to load model
loadModel <- function(modelPath){
  return(readRDS(modelPath))
}

#Function to compare file header
checkFileHeader <- function(fixed_header, file_header){
  return(all(fixed_header==file_header))
}

#Function to find unMatched columns
checkUnmatchedHeader <- function(fixed_header, file_header){
  return(match(fixed_header, file_header))
}

#Load train data for factor levels
CTDF.dev = readRDS('~/Port Recon/Deployment/PortfolioRecon_project/model/port_rec_training_v0.rds')

#Load trioptima header format file
trioptimaFileHeader = read.xlsx('utility/TriOptimaFileFormat.xlsx', sheet="Sheet1", colNames=TRUE)

#Read input files
#triOptimaPath = choose.files(caption = "Select TriOptima File", multi=FALSE)
#exManPath = choose.files(caption = "Select ExMan File", multi=FALSE)

triOptimaPath = '//NPNQ11P20110a/aarora33$/Documents/Port Recon/Deployment/PortfolioRecon_project/input_files/TriOptima 26032019.xlsx'
exManPath = '//NPNQ11P20110a/aarora33$/Documents/Port Recon/Deployment/PortfolioRecon_project/input_files/Exman 26032019.xlsx'
#triOptimaPath = '//NPNQ11P20110a/aarora33$/Documents/Port Recon/Deployment/PortfolioRecon_project/input_files/trioptima_data/TriOptima.xlsx'
#exManPath = '//NPNQ11P20110a/aarora33$/Documents/Port Recon/Deployment/PortfolioRecon_project/input_files/exman_data/Exman.xlsx'

now <- Sys.time()
print(paste("start time ", now))

#Cosolidate trioptima data

#columns used for analysis
triOptima_cols = c("MATCH_ID", "PARTY", "CP","TRADE_ID", "TRADE_ID2", "BOOK", "CP_TRADE_ID", 
             "PRODUCT_CLASS", "PRODUCT_CLASS_ORIG", "PAY_REC", "NOTIONAL", "CURR", "NOTIONAL2",
             "CURR2", "TRADE_DATE", "START_DATE", "END_DATE", "STRIKE_PRICE",
             "MTM_VALUE", "MTM_CURR", "MTM_DATE", "MTM_DIFF", "ABS_MTM_DIFF", 
             "MATCH_TYPE", "MATCH_SUBTYPE", "BREAK_DATE", "BREAK_AGE", "DIFF_DATE",
             "DIFF_AGE", "BREAK_CLOSE_DATE","BREAK_DESCRIPTION", "BREAK_ERROR_BY",
             "BREAK_ROOT_CAUSE", "BREAK_LAST_UPDATE", "COUNTERPARTY_NAME", "ASSET_CLASS",
             "PARTY_NAME", "CP_NAME", "CREATED_BY", "APPROVED_BY", "ATTACHMENT",
             "AGREEMENT_TYPE", "AGREEMENT_ID", "TRI_AGREEMENT_ID", "PARTY_GROUP",
             "PARTY_GROUP_NAME", "CP_GROUP", "CP_GROUP_NAME", "LEI", "CP_LEI",
             "CFTC_CATEGORY", "CP_CFTC_CATEGORY", "BREAK_WORKFLOW_STATUS",
             "MARGIN_TYPE")

triOptimaSheetNames = getSheetNames(triOptimaPath)
triOptimaData = data.frame()
#mydata <- read_excel(triOptimaPath, sheet = "LE")
for(sheet in triOptimaSheetNames){
  sheetData = read.xlsx(triOptimaPath, sheet=sheet, colNames=TRUE, skipEmptyRows = TRUE)
  sheetData = selectCol(sheetData, triOptima_cols)
  if (length(setdiff(triOptima_cols, colnames(sheetData))) == 0){
    sheetData = sheetData[,triOptima_cols]
    if(checkFileHeader(triOptima_cols, colnames(sheetData))){
      triOptimaData = rbind(triOptimaData, sheetData)
  }
    else{
      print(paste("**********File Headers Mismatch for Sheet",sheet,"**********"))
      stop("**********Program Interrupted**********")
  }
  }else {
    print(paste('Following Columns are not present ', setdiff(triOptima_cols, colnames(sheetData)), "in Sheet ", sheet))
    stop("**********Program Interrupted**********")
  }
}

#Cosolidate ExMan data
ExMan_cols = c("Match.Id", "Category")
exManSheetNames = getSheetNames(exManPath)
exManData = data.frame()
for(sheet in exManSheetNames){
  sheetData = read.xlsx(exManPath, sheet=sheet, colNames=TRUE, skipEmptyRows = TRUE)
  if (length(setdiff(ExMan_cols, colnames(sheetData))) == 0){
    sheetData = sheetData[,ExMan_cols]
    if(checkFileHeader(ExMan_cols, colnames(sheetData))){
      exManData = rbind(exManData, sheetData)
    }
    else{
      print(paste("**********File Headers Mismatch for Sheet",sheet,"**********"))
      stop("**********Program Interrupted**********")
    }
  }else {
    print(paste('Following Columns are not present ', setdiff(ExMan_cols, colnames(sheetData)), "in Sheet ", sheet))
    stop("**********Program Interrupted**********")
  }
  
}

#Vlookup trioptima and exman data
x = exManData[!duplicated(exManData$Match.Id),]
Topt_data_test = merge(triOptimaData, x[, c("Match.Id", "Category")], by.x = 'MATCH_ID', by.y = 'Match.Id')
#columns used for analysis
sel_cols = c("MATCH_ID", "PARTY", "CP","TRADE_ID", "TRADE_ID2", "BOOK", "CP_TRADE_ID", 
             "PRODUCT_CLASS", "PRODUCT_CLASS_ORIG", "PAY_REC", "NOTIONAL", "CURR", "NOTIONAL2",
             "CURR2", "TRADE_DATE", "START_DATE", "END_DATE", "STRIKE_PRICE",
             "MTM_VALUE", "MTM_CURR", "MTM_DATE", "MTM_DIFF", "ABS_MTM_DIFF", 
             "MATCH_TYPE", "MATCH_SUBTYPE", "BREAK_DATE", "BREAK_AGE", "DIFF_DATE",
             "DIFF_AGE", "BREAK_CLOSE_DATE","BREAK_DESCRIPTION", "BREAK_ERROR_BY",
             "BREAK_ROOT_CAUSE", "BREAK_LAST_UPDATE", "COUNTERPARTY_NAME", "ASSET_CLASS",
             "PARTY_NAME", "CP_NAME", "CREATED_BY", "APPROVED_BY", "ATTACHMENT",
             "AGREEMENT_TYPE", "AGREEMENT_ID", "TRI_AGREEMENT_ID", "PARTY_GROUP",
             "PARTY_GROUP_NAME", "CP_GROUP", "CP_GROUP_NAME", "LEI", "CP_LEI",
             "CFTC_CATEGORY", "CP_CFTC_CATEGORY", "BREAK_WORKFLOW_STATUS",
             "MARGIN_TYPE", "Category", "Issue.from",
             "Root.Cause")
Topt_data_test = selectCol(Topt_data_test, sel_cols)
dim(Topt_data_test)
#combining data into one row
temp_data = Topt_data_test
temp_data$MTM_VALUE = changeDatatype(temp_data$MTM_VALUE, 'numeric')
temp_data$NOTIONAL = changeDatatype(temp_data$NOTIONAL, 'numeric')
temp_data$NOTIONAL2 = changeDatatype(temp_data$NOTIONAL2, 'numeric')
temp_data$MTM_DIFF = changeDatatype(temp_data$MTM_DIFF, 'numeric')
temp_data$ABS_MTM_DIFF = changeDatatype(temp_data$ABS_MTM_DIFF, 'numeric')

myFreqs = temp_data %>% 
  group_by(MATCH_ID, PARTY) %>% 
  mutate(concat_TradeID = paste0(TRADE_ID, collapse = ","),
         concat_TRADEID2 = paste0(TRADE_ID2, collapse = ","),
         MTM_sum = sum(MTM_VALUE),
         NOTIONAL1_sum = sum(NOTIONAL),
         NOTIONAL2_sum = sum(NOTIONAL2),
         freq = n())
myFreqs = myFreqs[!duplicated(myFreqs[c(1,2)]),]
myFreqs = changeDatatype(myFreqs, 'dataframe')

myFreqs = myFreqs %>% 
  group_by(MATCH_ID) %>% 
  mutate(routes_per_matchID = n())

dual_entry = subset(myFreqs, myFreqs$routes_per_matchID == 2)
single_entry = subset(myFreqs, myFreqs$routes_per_matchID == 1)

#get Party data
party_data = subset(dual_entry, (dual_entry$PARTY == "CSI" | 
                                   dual_entry$PARTY == "CSSE" |
                                   dual_entry$PARTY == "CSX"|
                                   dual_entry$PARTY == "CSBDL"|
                                   dual_entry$PARTY == "CSE"))
party_data = rbind(party_data, single_entry)

#get Counter Party data
cp_data = subset(dual_entry, (dual_entry$PARTY != "CSI" & 
                                dual_entry$PARTY != "CSSE" &
                                dual_entry$PARTY != "CSX" &
                                dual_entry$PARTY != "CSBDL" &
                                dual_entry$PARTY != "CSE"))

#Adding more cols here
cp_cols = c("MATCH_ID", "PARTY", "CP" ,"PRODUCT_CLASS_ORIG", "CURR","CURR2", "TRADE_DATE", 
            "START_DATE", "END_DATE", "MTM_CURR", "PARTY_NAME",
            "CP_NAME", "concat_TradeID", "MTM_sum", "NOTIONAL1_sum",
            "NOTIONAL2_sum", "AGREEMENT_ID","AGREEMENT_TYPE", "freq")

#Single entry for Party and CPTY and create new vars from CPTY
combined_testdata = merge(x = party_data , y = cp_data[ , cp_cols], by = "MATCH_ID", all.x = TRUE)
combined_testdata$PARTY.x <- factor(combined_testdata$PARTY.x)

#Converting datatype
combined_testdata$TRADE_DATE.x = changeDatatype(combined_testdata$TRADE_DATE.x, 'date')
combined_testdata$START_DATE.x = changeDatatype(combined_testdata$START_DATE.x, 'date')
combined_testdata$END_DATE.x = changeDatatype(combined_testdata$END_DATE.x, 'date')
combined_testdata$MTM_DATE = changeDatatype(combined_testdata$MTM_DATE, 'date')
combined_testdata$BREAK_DATE =changeDatatype(combined_testdata$BREAK_DATE, 'date')
combined_testdata$BREAK_LAST_UPDATE = changeDatatype(combined_testdata$BREAK_LAST_UPDATE, 'date')
combined_testdata$TRADE_DATE.y = changeDatatype(combined_testdata$TRADE_DATE.y, 'date')
combined_testdata$START_DATE.y = changeDatatype(combined_testdata$START_DATE.y, 'date')
combined_testdata$END_DATE.y = changeDatatype(combined_testdata$END_DATE.y, 'date')

#Delete columns list which are maximum NA
del_cols = c("CP_TRADE_ID", "BREAK_CLOSE_DATE", "START_DATE.x",
             "BREAK_ROOT_CAUSE", "CP_CFTC_CATEGORY", "CREATED_BY", "START_DATE.y",
             "CFTC_CATEGORY", "TRADE_ID2", "STRIKE_PRICE",
             "APPROVED_BY", "BREAK_DESCRIPTION", "DIFF_DATE", "CP_LEI", "DIFF_AGE", 
             "BREAK_WORKFLOW_STATUS", "BREAK_ERROR_BY", "BREAK_LAST_UPDATE"
)
combined_testdata = deleteCol(combined_testdata, del_cols)
dim(combined_testdata)
#------------------------Feature Engineering and EDA--------------------

combined_testdata$NOTIONAL2_sum.x[is.na(combined_testdata$NOTIONAL2_sum.x)] = 0
combined_testdata$NOTIONAL1_sum.y[is.na(combined_testdata$NOTIONAL1_sum.y)] = 0
combined_testdata$NOTIONAL2_sum.y[is.na(combined_testdata$NOTIONAL2_sum.y)] = 0

#1. Create Total_Notional.x and Total_Notional.y variable
combined_testdata$total_notional.x = combined_testdata$NOTIONAL1_sum.x + combined_testdata$NOTIONAL2_sum.x
combined_testdata$total_notional.y = combined_testdata$NOTIONAL1_sum.y + combined_testdata$NOTIONAL2_sum.y
combined_testdata = deleteCol(combined_testdata, c("NOTIONAL", "NOTIONAL2", "NOTIONAL1_sum.x", "NOTIONAL2_sum.x" ,"NOTIONAL1_sum.y", "NOTIONAL2_sum.y"))

#2.create variable party cs or non cs
combined_testdata$CS_or_not.x = ifelse((combined_testdata$PARTY.x == "CSI" | combined_testdata$PARTY.x == "CSSE" | combined_testdata$PARTY.x == "CSX" ), "CS", "Non-CS")
combined_testdata$CS_or_not.y = ifelse((combined_testdata$PARTY.y == "CSI" | combined_testdata$PARTY.y == "CSSE" | combined_testdata$PARTY.y == "CSX" ), "CS", "Non-CS")

#3. Create party_mismatch and cpty_mismatch variable
combined_testdata$cp_mismatch = ifelse((changeDatatype(combined_testdata$CP.x, 'vector') == changeDatatype(combined_testdata$PARTY.y, 'vector')), "pty_match", "pty_mismatch")
combined_testdata = deleteCol(combined_testdata, c("PARTY_GROUP", "CP_GROUP", "PARTY_GROUP_NAME", "CP_GROUP_NAME", "PARTY.x", "CP.x", "PARTY.y", "CP.y"))

#4. Absolute MTM_diff
combined_testdata$MTM_DIFF_abs = abs(combined_testdata$MTM_DIFF)
combined_testdata = deleteCol(combined_testdata, c("MTM_DIFF"))

#5. MTM_Variables: -if MTM val is in same direct (+ve or -ve) etc
combined_testdata$MTM_direction.x = ifelse(combined_testdata$MTM_sum.x >= 0,"positive","negative")
combined_testdata$MTM_direction.y = ifelse(combined_testdata$MTM_sum.y >= 0, "positive","negative")

#6. 
combined_testdata$MTM_1mn = ifelse(combined_testdata$MTM_DIFF_abs >= 1000000,"above_1mn","below_1mn")
combined_testdata$MTM_200k = ifelse(combined_testdata$MTM_DIFF_abs >= 200000,"above_200k","below_200k")

#7. 
combined_testdata$MTM_direction = ifelse( (combined_testdata$MTM_sum.x >= 0 & combined_testdata$MTM_sum.y >= 0), "same_direction",
                                          ifelse( (combined_testdata$MTM_sum.x < 0 & combined_testdata$MTM_sum.y < 0), "same_direction",
                                                  ifelse( (combined_testdata$MTM_sum.x >= 0 & combined_testdata$MTM_sum.y < 0), "diff_direction",
                                                          ifelse( (combined_testdata$MTM_sum.x < 0 & combined_testdata$MTM_sum.y >= 0), "diff_direction", "Unkn"
                                                          )))
)

#8. MTM_0 from which side
combined_testdata$MTM_0 = 
  ifelse( (combined_testdata$MTM_sum.x == 0 & combined_testdata$MTM_sum.y == 0 ), "both_mtm_0",
          ifelse( (combined_testdata$MTM_sum.x == 0 ), "party_mtm_0",
                  ifelse( (combined_testdata$MTM_sum.y == 0), "cpty_mtm_0", "mtm_non_zero"
                  )))

#9. Same product class or not
combined_testdata$product_mismatch = ifelse((changeDatatype(combined_testdata$PRODUCT_CLASS_ORIG.x, 'vector') == changeDatatype(combined_testdata$PRODUCT_CLASS_ORIG.y, 'vector')), "product_match", "product_mismatch")

#10. Same Aggrement Type or not
combined_testdata$Agmt_type_mismatch = ifelse((changeDatatype(combined_testdata$AGREEMENT_TYPE.x, 'vector') == changeDatatype(combined_testdata$AGREEMENT_TYPE.y, 'vector')), "Agmt_type_match", "Agmt_type_mismatch")

#11. Same Aggrement ID or not
combined_testdata$Agmt_ID_mismatch = ifelse((changeDatatype(combined_testdata$AGREEMENT_ID.x, 'vector') == changeDatatype(combined_testdata$AGREEMENT_ID.y, 'vector')), "Agmt_id_match", "Agmt_id_mismatch")

#Adding NA and extreme values for single entry routes
#Impute single entry factor cols with single entry
factor_cols = c("PRODUCT_CLASS_ORIG.y", "CURR.y", "CURR2.y","MTM_CURR.y",
                "PARTY_NAME.y", "CP_NAME.y", "AGREEMENT_TYPE.y","CS_or_not.y", "cp_mismatch",
                "MTM_direction.y", "product_mismatch","MTM_direction", "MTM_0", "Agmt_type_mismatch",
                "Agmt_ID_mismatch", "MTM_1mn", "MTM_200k"
)

for(i in factor_cols) {
  levels(combined_testdata[,i]) <- c(levels(combined_testdata[,i]), "single_entry")
  combined_testdata[is.na(combined_testdata$freq.y),][,i] = "single_entry"
}

#Impute single entry numeric cols with extreme values
combined_testdata[is.na(combined_testdata$freq.y),]$MTM_sum.y = -9999999
combined_testdata[is.na(combined_testdata$freq.y),]$freq.y = 0
combined_testdata[is.na(combined_testdata$Agmt_ID_mismatch),]$Agmt_ID_mismatch = "NA"

#List of columns which we are using for anlysis
col_for_analysis = c("MATCH_ID","concat_TradeID.x","concat_TradeID.y","PARTY_NAME.x","TRADE_ID", "PRODUCT_CLASS",
                     "CURR.x", "MTM_CURR.x", "ABS_MTM_DIFF","MATCH_TYPE", "MATCH_SUBTYPE",
                     "BREAK_AGE", "ASSET_CLASS", "ATTACHMENT", "AGREEMENT_TYPE.x",
                     "Category", "Issue.from", "Root.Cause", "MTM_sum.x", "freq.x",
                     "routes_per_matchID", "product_mismatch",
                     "CURR.y", "MTM_CURR.y", "AGREEMENT_TYPE.y",
                     "MTM_sum.y", "freq.y", "total_notional.x", "total_notional.y",
                     "CS_or_not.x", "CS_or_not.y", "cp_mismatch", "MTM_direction.x",
                     "MTM_direction", "MTM_direction.y", "MTM_0",
                     "MTM_DIFF_abs", "Agmt_type_mismatch","Agmt_ID_mismatch", 
                     "MTM_1mn", "MTM_200k"
)
combined_testdata = selectCol(combined_testdata, col_for_analysis)

#Imputing NA with mode value
if (dim(combined_testdata[(is.na(combined_testdata$CURR.y)),])[1] != 0) {
  combined_testdata[(is.na(combined_testdata$CURR.y)),]$CURR.y = Mode(CTDF.dev$CURR.y)
}
if (dim(combined_testdata[(is.na(combined_testdata$CURR.x)),])[1] != 0) {
  combined_testdata[(is.na(combined_testdata$CURR.x)),]$CURR.x = Mode(CTDF.dev$CURR.x)
}
if (dim(combined_testdata[(is.na(combined_testdata$BREAK_AGE)),])[1] != 0) {
  combined_testdata[(is.na(combined_testdata$BREAK_AGE)),]$BREAK_AGE = Mode(CTDF.dev$BREAK_AGE)  
}
if (dim(combined_testdata[(is.na(combined_testdata$concat_TradeID.y)),])[1] != 0) {
   combined_testdata[(is.na(combined_testdata$concat_TradeID.y)),]$concat_TradeID.y = "NA"
}


#Drop rest of the na rows
combined_testdata = na.omit(combined_testdata)

#---------------------------------Predictions------------------------------

#Convert column to factor
combined_testdata=combined_testdata %>% mutate_if(is.character, as.factor)
combined_testdata$PRODUCT_CLASS <- convertToFactor(combined_testdata$PRODUCT_CLASS, levels=levels(CTDF.dev$PRODUCT_CLASS))
combined_testdata$CURR.x <- convertToFactor(combined_testdata$CURR.x, levels=levels(CTDF.dev$CURR.x))
combined_testdata$MTM_CURR.x <- convertToFactor(combined_testdata$MTM_CURR.x, levels=levels(CTDF.dev$MTM_CURR.x))
combined_testdata$MATCH_TYPE <- convertToFactor(combined_testdata$MATCH_TYPE, levels=levels(CTDF.dev$MATCH_TYPE))
combined_testdata$MATCH_SUBTYPE <- convertToFactor(combined_testdata$MATCH_SUBTYPE, levels=levels(CTDF.dev$MATCH_SUBTYPE))
combined_testdata$BREAK_AGE <- convertToFactor(combined_testdata$BREAK_AGE, levels=levels(CTDF.dev$BREAK_AGE))
combined_testdata$ASSET_CLASS <- convertToFactor(combined_testdata$ASSET_CLASS, levels=levels(CTDF.dev$ASSET_CLASS))
combined_testdata$AGREEMENT_TYPE.x <- convertToFactor(combined_testdata$AGREEMENT_TYPE.x, levels=levels(CTDF.dev$AGREEMENT_TYPE.x))
combined_testdata$Category <- convertToFactor(combined_testdata$Category, levels=levels(CTDF.dev$Category))
combined_testdata$CURR.y <- convertToFactor(combined_testdata$CURR.y, levels=levels(CTDF.dev$CURR.y))
combined_testdata$MTM_CURR.y <- convertToFactor(combined_testdata$MTM_CURR.y, levels=levels(CTDF.dev$MTM_CURR.y))
combined_testdata$AGREEMENT_TYPE.y <- convertToFactor(combined_testdata$AGREEMENT_TYPE.y, levels=levels(CTDF.dev$AGREEMENT_TYPE.y))
combined_testdata$MTM_0 <- convertToFactor(combined_testdata$MTM_0, levels=levels(CTDF.dev$MTM_0))

combined_testdata$product_mismatch <- convertToFactor(combined_testdata$product_mismatch, levels=levels(CTDF.dev$product_mismatch))
combined_testdata$Agmt_type_mismatch <- convertToFactor(combined_testdata$Agmt_type_mismatch, levels=levels(CTDF.dev$Agmt_type_mismatch))
combined_testdata$Agmt_ID_mismatch <- convertToFactor(combined_testdata$Agmt_ID_mismatch, levels=levels(CTDF.dev$Agmt_ID_mismatch))

combined_testdata$MTM_1mn <- convertToFactor(combined_testdata$MTM_1mn, levels=levels(CTDF.dev$MTM_1mn))
combined_testdata$MTM_200k <- convertToFactor(combined_testdata$MTM_200k, levels=levels(CTDF.dev$MTM_200k))
combined_testdata$MTM_direction <- convertToFactor(combined_testdata$MTM_direction, levels=levels(CTDF.dev$MTM_direction))
combined_testdata$CS_or_not.x <- convertToFactor(combined_testdata$CS_or_not.x, levels=levels(CTDF.dev$CS_or_not.x))
combined_testdata$CS_or_not.y <- convertToFactor(combined_testdata$CS_or_not.y, levels=levels(CTDF.dev$CS_or_not.y))
combined_testdata$cp_mismatch <- convertToFactor(combined_testdata$cp_mismatch, levels=levels(CTDF.dev$cp_mismatch))

combined_testdata$MTM_direction.x <- convertToFactor(combined_testdata$MTM_direction.x, levels=levels(CTDF.dev$MTM_direction.x))
combined_testdata$MTM_direction.y <- convertToFactor(combined_testdata$MTM_direction.y, levels=levels(CTDF.dev$MTM_direction.y))
#-----------SVM----------------------------------
#------------------------------------------------
print("**********Prediction started for Issue Pending From**********")

dim(combined_testdata)
#Subset of dataframe which we are not providing prediction
x_na = combined_testdata[rowSums(is.na(combined_testdata)) > 0,]
x_na$Predicted.Issue.Pending.from = 'Manual'

#Subset of dataframe which will pass to the model
x = na.omit(combined_testdata)
View(x[,-c(1,2,11,15,21)])
str(x[,-c(1,2,11,15,21)])
#Loading ML model
svm_model <- loadModel("~/Port Recon/Deployment/PortfolioRecon_project/model/svm_model_v0")
x$Predicted.Issue.Pending.from = predict(svm_model, x[,-c(1,2,11,15,21)])

print("**********Prediction completed for Issue Pending From**********")

#Combining dataframe
final_result = rbind(x, x_na)

#Write output to excel file
write.xlsx(final_result, paste("output_files/PortRecOutput_",gsub(":", "", Sys.time()),".xlsx", sep=""))

print("**********Output file created successfully in output_files folder**********")
print("**********Execution completed**********")

then <- Sys.time()
print(paste("End time ", then))
print(paste("Time taken in minutes ", (then - now)/60))