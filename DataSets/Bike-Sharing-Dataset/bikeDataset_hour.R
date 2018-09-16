dataset = read.csv('hour.csv')
summary(dataset)
library(caTools)
set.seed(123)

split = sample.split(dataset$cnt, SplitRatio = 0.8)
  training_set = subset(dataset, split == TRUE)
training_set = training_set[,c(3:17)]
test_set = subset(dataset, split == FALSE)
test_set = test_set[,c(3:17)]
cor(training_set$cnt, training_set)

#Backward Elimination all variables
regressor = lm(formula = cnt ~ season + yr + mnth + hr + holiday + weekday + 
                 workingday + weathersit + temp + atemp + hum + windspeed + 
                 casual + registered,
               data = training_set)
summary(regressor)

#removing weekday
regressor = lm(formula = cnt ~ season + yr + mnth + hr + holiday + 
                 workingday + weathersit + temp + atemp + hum + windspeed + 
                 casual + registered,
               data = training_set)
summary(regressor)

#removing windspeed
regressor = lm(formula = cnt ~ season + yr + mnth + hr + holiday + 
                 workingday + weathersit + temp + atemp + hum +
                 casual + registered,
               data = training_set)
summary(regressor)


#removing temp
regressor = lm(formula = cnt ~ season + yr + mnth + hr + holiday + 
                 workingday + weathersit + atemp + hum +
                 casual + registered,
               data = training_set)
summary(regressor)

#removing casual and registered
regressor = lm(formula = cnt ~ season + yr + mnth + hr + holiday + 
                 workingday + weathersit + atemp + hum,
               data = training_set)
summary(regressor)

#removing month
regressor = lm(formula = cnt ~ season + yr + hr + holiday + 
                 workingday + weathersit + atemp + hum,
               data = training_set)
summary(regressor)

#removing weathersit
regressor = lm(formula = cnt ~ season + yr + hr + holiday + 
                 workingday + atemp + hum,
               data = training_set)
summary(regressor)

#removing workingday also Final Model
regressor = lm(formula = cnt ~ season + yr + hr + holiday + atemp + hum,
               data = training_set)
summary(regressor)

#plot(training_set$atemp, training_set$hum)

#Prediction
y_pred = predict(regressor, newdata = test_set)
View(y_pred)
type(y_pred)
typeof(y_pred)
View(test_set$cnt)
