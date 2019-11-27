import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

class Label_Encoder():
    def __init__(self, vertical, input_train_df, input_test_df):
        self.vertical = vertical
        self.input_train_df = input_train_df
        self.input_test_df = input_test_df
    
    def labelEncoderFit(self):
        le_Education_Field = LabelEncoder()
        le_isNative = LabelEncoder()
        if self.vertical != 'FM':
            le_underTraining = LabelEncoder()
        le_Office_location = LabelEncoder()
        le_Program = LabelEncoder()
        le_Manager_Designation = LabelEncoder()
        le_Designation = LabelEncoder()
        le_Last_Year_Rating = LabelEncoder()
        le_Previous_Last_Year_Rating = LabelEncoder()
        le_Channel = LabelEncoder()
        le_Manager_Rating = LabelEncoder()
        le_Salary_Rank = LabelEncoder()

        le_Education_Field.fit(self.input_train_df['Education Field'])
        le_isNative.fit(self.input_train_df['Is office located in the native state'])
        if self.vertical != 'FM':
            le_underTraining.fit(self.input_train_df['Is Employee under Training Agreement / CEP'])
        le_Office_location.fit(self.input_train_df['Office location'])
        le_Program.fit(self.input_train_df['Program'])
        le_Manager_Designation.fit(self.input_train_df['Manager Designation'])
        le_Designation.fit(self.input_train_df['Designation'])
        le_Last_Year_Rating.fit(self.input_train_df['Last Year Rating'])
        le_Previous_Last_Year_Rating.fit(self.input_train_df['Previous Last Year Rating'])
        le_Channel.fit(self.input_train_df['Channel'])
        le_Manager_Rating.fit(self.input_train_df['Manager Rating'])
        le_Salary_Rank.fit(self.input_train_df['Salary Rank'])

        pickle_path = r'C:\Users\chinmay.shelke\Downloads\Projects\AttritionPrediction\NewCode\Final_v1\pickles\\'
        joblib.dump(le_Education_Field, open(pickle_path + str(self.vertical) + '_le_Education_Field.joblib', 'wb'))  
        joblib.dump(le_isNative, open(pickle_path + str(self.vertical) + '_le_isNative.joblib', 'wb'))
        if self.vertical != 'FM':
            joblib.dump(le_underTraining, open(pickle_path + str(self.vertical) + '_le_underTraining.joblib', 'wb'))  
        joblib.dump(le_Office_location, open(pickle_path + str(self.vertical) + '_le_Office_location.joblib', 'wb'))  
        joblib.dump(le_Program, open(pickle_path + str(self.vertical) + '_le_Program.joblib', 'wb'))  
        joblib.dump(le_Manager_Designation, open(pickle_path + str(self.vertical) + '_le_Manager_Designation.joblib', 'wb'))  
        joblib.dump(le_Designation, open(pickle_path + str(self.vertical) + '_le_Designation.joblib', 'wb'))  
        joblib.dump(le_Last_Year_Rating, open(pickle_path + str(self.vertical) + '_le_Last_Year_Rating.joblib', 'wb'))  
        joblib.dump(le_Previous_Last_Year_Rating, open(pickle_path + str(self.vertical) + '_le_Previous_Last_Year_Rating.joblib', 'wb'))  
        joblib.dump(le_Channel, open(pickle_path + str(self.vertical) + '_le_Channel.joblib', 'wb'))  
        joblib.dump(le_Manager_Rating, open(pickle_path + str(self.vertical) + '_le_Manager_Rating.joblib', 'wb'))  
        joblib.dump(le_Salary_Rank, open(pickle_path + str(self.vertical) + '_le_Salary_Rank.joblib', 'wb'))

        self.input_train_df['Education Field'] = le_Education_Field.transform(self.input_train_df['Education Field'])
        self.input_train_df['Is office located in the native state'] = le_isNative.transform(self.input_train_df['Is office located in the native state'])
        if self.vertical != 'FM':
            self.input_train_df['Is Employee under Training Agreement / CEP'] = le_underTraining.transform(self.input_train_df['Is Employee under Training Agreement / CEP'])
        self.input_train_df['Office location'] = le_Office_location.transform(self.input_train_df['Office location'])
        self.input_train_df['Program'] = le_Program.transform(self.input_train_df['Program'])
        self.input_train_df['Manager Designation'] = le_Manager_Designation.transform(self.input_train_df['Manager Designation'])
        self.input_train_df['Designation'] = le_Designation.transform(self.input_train_df['Designation'])
        self.input_train_df['Last Year Rating'] = le_Last_Year_Rating.transform(self.input_train_df['Last Year Rating'])
        self.input_train_df['Previous Last Year Rating'] = le_Previous_Last_Year_Rating.transform(self.input_train_df['Previous Last Year Rating'])
        self.input_train_df['Channel'] = le_Channel.transform(self.input_train_df['Channel'])
        self.input_train_df['Manager Rating'] = le_Manager_Rating.transform(self.input_train_df['Manager Rating'])
        self.input_train_df['Salary Rank'] = le_Salary_Rank.transform(self.input_train_df['Salary Rank'])
        return self.input_train_df

    def labelEncoderTest(self):
        
        
        pickle_path = r'C:\Users\chinmay.shelke\Downloads\Projects\AttritionPrediction\NewCode\Final_v1\pickles\\'
        le_Education_Field = joblib.load(open(pickle_path + str(self.vertical) + '_le_Education_Field.joblib', 'rb'))
        le_isNative = joblib.load(open(pickle_path + str(self.vertical) + '_le_isNative.joblib', 'rb'))
        if self.vertical != 'FM':
            le_underTraining = joblib.load(open(pickle_path + str(self.vertical) + '_le_underTraining.joblib', 'rb'))  
            self.input_test_df['Is Employee under Training Agreement / CEP'] = self.input_test_df['Is Employee under Training Agreement / CEP'].map(lambda s: '<unknown>' if s not in le_underTraining.classes_ else s)
            le_underTraining.classes_ = np.append(le_underTraining.classes_, '<unknown>')
            self.input_test_df['Is Employee under Training Agreement / CEP'] = le_underTraining.transform(self.input_test_df['Is Employee under Training Agreement / CEP'])
        le_Office_location = joblib.load(open(pickle_path + str(self.vertical) + '_le_Office_location.joblib', 'rb'))  
        le_Program = joblib.load(open(pickle_path + str(self.vertical) + '_le_Program.joblib', 'rb'))
        le_Manager_Designation = joblib.load(open(pickle_path + str(self.vertical) + '_le_Manager_Designation.joblib', 'rb'))
        le_Designation = joblib.load(open(pickle_path + str(self.vertical) + '_le_Designation.joblib', 'rb'))
        le_Last_Year_Rating = joblib.load(open(pickle_path + str(self.vertical) + '_le_Last_Year_Rating.joblib', 'rb'))
        le_Previous_Last_Year_Rating = joblib.load(open(pickle_path + str(self.vertical) + '_le_Previous_Last_Year_Rating.joblib', 'rb'))
        le_Channel = joblib.load(open(pickle_path + str(self.vertical) + '_le_Channel.joblib', 'rb'))
        le_Manager_Rating = joblib.load(open(pickle_path + str(self.vertical) + '_le_Manager_Rating.joblib', 'rb'))
        le_Salary_Rank = joblib.load(open(pickle_path + str(self.vertical) + '_le_Salary_Rank.joblib', 'rb'))
        
        
        self.input_test_df['Education Field'] = self.input_test_df['Education Field'].map(lambda s: '<unknown>' if s not in le_Education_Field.classes_ else s)
        le_Education_Field.classes_ = np.append(le_Education_Field.classes_, '<unknown>')
        self.input_test_df['Education Field'] = le_Education_Field.transform(self.input_test_df['Education Field'])
        
        self.input_test_df['Is office located in the native state'] = self.input_test_df['Is office located in the native state'].map(lambda s: '<unknown>' if s not in le_isNative.classes_ else s)
        le_isNative.classes_ = np.append(le_isNative.classes_, '<unknown>')
        self.input_test_df['Is office located in the native state'] = le_isNative.transform(self.input_test_df['Is office located in the native state'])
        
        self.input_test_df['Office location'] = self.input_test_df['Office location'].map(lambda s: '<unknown>' if s not in le_Office_location.classes_ else s)
        le_Office_location.classes_ = np.append(le_Office_location.classes_, '<unknown>')
        self.input_test_df['Office location'] = le_Office_location.transform(self.input_test_df['Office location'])

        self.input_test_df['Program'] = self.input_test_df['Program'].map(lambda s: '<unknown>' if s not in le_Program.classes_ else s)
        le_Program.classes_ = np.append(le_Program.classes_, '<unknown>')
        self.input_test_df['Program'] = le_Program.transform(self.input_test_df['Program'])

        self.input_test_df['Manager Designation'] = self.input_test_df['Manager Designation'].map(lambda s: '<unknown>' if s not in le_Manager_Designation.classes_ else s)
        le_Manager_Designation.classes_ = np.append(le_Manager_Designation.classes_, '<unknown>')
        self.input_test_df['Manager Designation'] = le_Manager_Designation.transform(self.input_test_df['Manager Designation'])

        self.input_test_df['Designation'] = self.input_test_df['Designation'].map(lambda s: '<unknown>' if s not in le_Designation.classes_ else s)
        le_Designation.classes_ = np.append(le_Designation.classes_, '<unknown>')
        self.input_test_df['Designation'] = le_Designation.transform(self.input_test_df['Designation'])

        self.input_test_df['Last Year Rating'] = self.input_test_df['Last Year Rating'].map(lambda s: '<unknown>' if s not in le_Last_Year_Rating.classes_ else s)
        le_Last_Year_Rating.classes_ = np.append(le_Last_Year_Rating.classes_, '<unknown>')
        self.input_test_df['Last Year Rating'] = le_Last_Year_Rating.transform(self.input_test_df['Last Year Rating'])

        self.input_test_df['Previous Last Year Rating'] = self.input_test_df['Previous Last Year Rating'].map(lambda s: '<unknown>' if s not in le_Previous_Last_Year_Rating.classes_ else s)
        le_Previous_Last_Year_Rating.classes_ = np.append(le_Previous_Last_Year_Rating.classes_, '<unknown>')
        self.input_test_df['Previous Last Year Rating'] = le_Previous_Last_Year_Rating.transform(self.input_test_df['Previous Last Year Rating'])

        self.input_test_df['Channel'] = self.input_test_df['Channel'].map(lambda s: '<unknown>' if s not in le_Channel.classes_ else s)
        le_Channel.classes_ = np.append(le_Channel.classes_, '<unknown>')
        self.input_test_df['Channel'] = le_Channel.transform(self.input_test_df['Channel'])

        self.input_test_df['Manager Rating'] = self.input_test_df['Manager Rating'].map(lambda s: '<unknown>' if s not in le_Manager_Rating.classes_ else s)
        le_Manager_Rating.classes_ = np.append(le_Manager_Rating.classes_, '<unknown>')
        self.input_test_df['Manager Rating'] = le_Manager_Rating.transform(self.input_test_df['Manager Rating'])

        self.input_test_df['Salary Rank'] = self.input_test_df['Salary Rank'].map(lambda s: '<unknown>' if s not in le_Salary_Rank.classes_ else s)
        le_Salary_Rank.classes_ = np.append(le_Salary_Rank.classes_, '<unknown>')
        self.input_test_df['Salary Rank'] = le_Salary_Rank.transform(self.input_test_df['Salary Rank'])

        return self.input_test_df

