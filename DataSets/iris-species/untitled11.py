import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style='white', color_codes=True)
iris_original = pd.read_csv('Iris.csv')
iris = iris_original.copy()
iris = iris.drop('Id', axis=1)
import numpy as np

iris.columns.values

iris_class =  ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]
iris_class[0]

for i in range(0,4) :
    for j in range(0,3) : 
        print("***Boxplot for " + iris.columns.values[i] + " and " + iris_class[j])
        data = iris[iris.columns.values[i]][iris.Species == iris_class[j]]
        #print("Median : ", np.median(data))
        boxfox = plt.boxplot(data, showfliers=True)
        print('Whiskers: ', [item.get_ydata()[1] for item in boxfox['whiskers']])
        x = [item.get_ydata() for item in boxfox['fliers']]
        print('Outliers: ', x[0])
        if len(x[0] > 0) :
            print(x[0])
            for k in range(0, len(x[0])) : 
                #print("ol for " , data)
                print("outliers ",  x[0][k])
                data.replace(x[0][k], np.median(data),inplace=True)
                print("bla", iris[iris.columns.values[i]][iris.Species == iris_class[j]])
        plt.pause(0.05)      
        