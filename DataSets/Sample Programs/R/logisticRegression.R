quality = read.csv('quality.csv')
head(quality)
str(quality)
table(quality$PoorCare)
prop.table(table(quality$PoorCare))
library(caTools)
set.seed(20)
spl = sample.split(quality$PoorCare, SplitRatio = 0.70)
table(spl)
train = subset(quality, spl == TRUE)
test = subset(quality, spl == FALSE)
nrow(train);
nrow(test)

prop.table(table(train$PoorCare))
prop.table(table(test$PoorCare))

#Logistic model
logreg = glm(PoorCare ~ OfficeVisits + Narcotics,
             data = train,
             family = "binomial")
summary(logreg)

logreg = glm(PoorCare ~ OfficeVisits + Narcotics + TotalVisits,
             data = train,
             family = "binomial")
summary(logreg)

cor(quality$OfficeVisits, quality$TotalVisits)

logreg = glm(PoorCare ~ Narcotics + TotalVisits,
             data = train,
             family = "binomial")
summary(logreg)
names(train)
mod <- glm(train$PoorCare ~.-MemberID,
           data = train,
           family = "binomial")


library(MASS)
stepAIC(mod)
summary(mod)

mod <- glm(formula = train$PoorCare ~ OfficeVisits + Narcotics + DaysSinceLastERVisit + 
      ClaimLines + StartedOnCombination + AcuteDrugGapSmall, family = "binomial", 
    data = train)
summary(mod)

x = stepAIC(mod)
predtrain = predict(x, type = "response")
predtrain
tapply(predtrain, train$PoorCare, mean)


predtest = predict(x, newdata = test,
                   type = "response")
predtest


#ROC CURVE
library(ROCR)
ROCR=prediction(predtrain,train$PoorCare)
perf=performance(ROCR,"tpr","fpr")
plot(perf,colorize=T,print.cutoffs.at=seq(0,1,0.1),text.adj=c(-0.2,1.7))
perf=performance(ROCR,"auc")


a = table(test$PoorCare, predtest >= 0.5)
accuracy <- sum(diag(a)/nrow(test))
accuracy
#Calculate sensitivity specificity and others from a

install.packages("caret")
library(caret)
confusionMatrix()

