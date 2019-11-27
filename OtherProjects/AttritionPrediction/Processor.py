import pandas as pd
import numpy as np


class Processor:

    def __init__(self, input_df, vertical):
        self.input_df = input_df
        self.vertical = vertical
        path = r'C:\Users\chinmay.shelke\Downloads\Projects\AttritionPrediction\FinalData\Raw\Train'
        self.co_train_df = pd.read_excel(path + '\CO_Jan16_Dec18.xlsx')
        self.fm_train_df = pd.read_excel(path + '\FM_Jan16_Dec18.xlsx')
        self.di_train_df = pd.read_excel(path + '\DI_Jan16_Dec18.xlsx')
        self.ss_train_df = pd.read_excel(path + '\SS_Jan16_Dec18.xlsx')
        self.input_df_copy = self.input_df.copy()

    def combined_preprocessor(self):
        
        columns_drop = ['Employee Id', 'Employee Code', 'Employee Name', 'BLI Process', 'vcrSubFunction', 'vcrFunction', 
                        'Birth Date', 'Job Role id', 'Joing Date', 'Last Working Day', 'Employee Status', 
                        'Time to Commute to Office', 'Vertical', 'Manager', 'Channel of hiring/Hiring type', 
                        'Source', 'Recruitment agency', 'Highest Qualification', 'Number of Months in the Current Process',
                        'Gender', 'Marital Status']
        
        for column in list(self.input_df.columns):
            if column in columns_drop:
                self.input_df = self.input_df.drop(column, axis=1)
        return self.input_df
    
    def vertical_preprocessor(self):
        if self.vertical == 'FM':
            self.input_df = self.fm_preprocessor()
        if self.vertical == 'CO':
            self.input_df = self.co_preprocessor()
        if self.vertical == 'DI':
            self.input_df = self.di_preprocessor()
        if self.vertical == 'SS':
            self.input_df = self.ss_preprocessor()
            
        return self.input_df
            

    def convert_to_bins(self, input_column, bins_list):
        input_column = pd.cut(input_column, bins_list)
        input_column = input_column.astype(str)
        return input_column

    def di_preprocessor(self) :
        if 'Age' not in self.input_df.columns:
            self.input_df['Age'] = 30
        if 'Manager Rating' not in self.input_df.columns:
            self.input_df['Manager Rating'] = 'Blanks'
        if 'Monetory Rewards in last 12 Months' not in self.input_df.columns:
            self.input_df['Monetory Rewards in last 12 Months'] = 0
        if 'Number Of training completed' not in self.input_df.columns:
            self.input_df['Number Of training completed'] = 0
        if 'Previous Last Year Rating' not in self.input_df.columns:
            self.input_df['Previous Last Year Rating'] = 'Blanks'
        if 'unplanned leaves in last 6 months' not in self.input_df.columns:
            self.input_df['unplanned leaves in last 6 months'] = 0
        self.input_df['Age'] = self.input_df['Age'].fillna(30)
        self.input_df['Age'] = self.input_df['Age'].astype('int')
        self.input_df['Average daily hours'] = self.input_df['Average daily hours'].fillna(9.5)
        self.input_df['Average daily hours'] = np.where(self.input_df['Average daily hours'] < 9.0, -1, self.input_df['Average daily hours'])
        self.input_df['Average daily hours'] = np.where(self.input_df['Average daily hours'] == 9.0, 0, self.input_df['Average daily hours'])
        self.input_df['Average daily hours'] = np.where(self.input_df['Average daily hours'] > 9.0, 1, self.input_df['Average daily hours'])
        self.input_df = self.input_df.drop(['No. of IJP postings applied'], axis = 1)
        self.input_df = self.input_df.drop(['No. of unavailed comp offs in last 6 months'], axis = 1)
        self.input_df['Loss of Pay in last 6 months'] = self.input_df['Loss of Pay in last 6 months'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'] = self.input_df['unplanned leaves in last 6 months'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'][self.input_df['unplanned leaves in last 6 months'] < 0] = 0
        self.input_df['Frequency of manager change'] = self.input_df['Frequency of manager change'].fillna(0)
        self.input_df['Number of Months in eClerx'] = self.input_df['Number of Months in eClerx'].fillna(0)
        self.input_df['Number of Months in eClerx'][self.input_df['Number of Months in eClerx'] < 0] = 0
        self.input_df['Number of Months in Current Designation'] = self.input_df['Number of Months in Current Designation'].fillna(0)
        self.input_df['Number of Months in Current Designation'][self.input_df['Number of Months in Current Designation'] < 0] = 0
        self.input_df = self.input_df.drop(['Awards for the Year'], axis = 1)
        self.input_df = self.input_df.drop(['Monetory Rewards in last 12 Months'], axis = 1)
        self.input_df['No. of companies worked'] = self.input_df['No. of companies worked'].fillna(0)
        self.input_df['Total working years'] = self.input_df['Total working years'].fillna(0)
        self.input_df['Total working years'][self.input_df['Total working years'] < 0] = 0
        self.input_df['Number Of training completed'] = self.input_df['Number Of training completed'].fillna(0)
        self.input_df = self.input_df.drop(['CCA'], axis = 1)
        self.input_df = self.input_df.drop(['Total working years'], axis = 1)
        self.input_df = self.input_df.drop(['Number of Months in Current Designation'], axis = 1)
        self.input_df = self.input_df.drop(['Loss of Pay in last 6 months'], axis = 1)

        tenure_bins = [-10, 12, 24, 36, 999]
        self.input_df['Number of Months in eClerx'] = self.convert_to_bins(self.input_df['Number of Months in eClerx'], tenure_bins)
        eclerx_tenure_mapper = {'(-10, 12]': 4, 
                              '(12, 24]': 3, 
                              '(24, 36]': 2, 
                              '(36, 999]': 1}
        self.input_df['Number of Months in eClerx'] = self.input_df['Number of Months in eClerx'].replace(eclerx_tenure_mapper)

        trainings_bins = [-10, 0, 10, 99]
        self.input_df['Number Of training completed'] = self.convert_to_bins(self.input_df['Number Of training completed'], trainings_bins)
        training_mapper = {'(-10, 0]': 1, 
                            '(0, 10]': 2, 
                            '(10, 99]': 3}
        self.input_df['Number Of training completed'] = self.input_df['Number Of training completed'].replace(training_mapper)
        categorical_cols = list(self.input_df.select_dtypes(include=['object']).columns)
        self.input_df[categorical_cols] = self.input_df[categorical_cols].fillna('Blanks')
        
        columns_seq_di = ['Education Field', 'Is office located in the native state', 'Average daily hours', 
                          'Is Employee under Training Agreement / CEP', 'Office location', 'unplanned leaves in last 6 months', 
                          'Program', 'Manager Designation', 'Frequency of manager change', 'Number of Months in eClerx', 'Designation', 
                          'Last Year Rating', 'Previous Last Year Rating', 'No. of companies worked', 'Channel', 'Age', 
                          'Number Of training completed', 'Manager Rating', 'Salary Rank']
        self.input_df = self.input_df[columns_seq_di]
        return self.input_df

    def ss_preprocessor(self):
        if 'Age' not in self.input_df.columns:
            self.input_df['Age'] = 30
        if 'Manager Rating' not in self.input_df.columns:
            self.input_df['Manager Rating'] = 'Blanks'
        if 'Monetory Rewards in last 12 Months' not in self.input_df.columns:
            self.input_df['Monetory Rewards in last 12 Months'] = 0
        if 'Number Of training completed' not in self.input_df.columns:
            self.input_df['Number Of training completed'] = 0
        if 'Previous Last Year Rating' not in self.input_df.columns:
            self.input_df['Previous Last Year Rating'] = 'Blanks'
        if 'unplanned leaves in last 6 months' not in self.input_df.columns:
            self.input_df['unplanned leaves in last 6 months'] = 0
        self.input_df['Age'] = self.input_df['Age'].fillna(30)
        self.input_df['Age'] = self.input_df['Age'].astype('int')
        self.input_df['Average daily hours'].value_counts(dropna=False)
        self.input_df['Average daily hours'] = self.input_df['Average daily hours'].fillna(9.5)
        self.input_df['No. of IJP postings applied'] = self.input_df['No. of IJP postings applied'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'] = self.input_df['unplanned leaves in last 6 months'].fillna(0)
        self.input_df['No. of unavailed comp offs in last 6 months'] = self.input_df['No. of unavailed comp offs in last 6 months'].fillna(0)
        self.input_df['Loss of Pay in last 6 months'] = self.input_df['Loss of Pay in last 6 months'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'][self.input_df['unplanned leaves in last 6 months']<0]=0
        self.input_df['Frequency of manager change'] = self.input_df['Frequency of manager change'].fillna(0)
        self.input_df['Awards for the Year'] = self.input_df['Awards for the Year'].fillna(0)
        self.input_df['Monetory Rewards in last 12 Months'] = self.input_df['Monetory Rewards in last 12 Months'].fillna(0)
        self.input_df['No. of companies worked'] = self.input_df['No. of companies worked'].fillna(0)
        self.input_df['Total working years'] = self.input_df['Total working years'].fillna(0)
        self.input_df['Number Of training completed'] = self.input_df['Number Of training completed'].fillna(0)
        self.input_df = self.input_df.drop(['CCA'], axis = 1)
        eclerx_tenure_bins = [-10, 12, 24, 36, 999]
        self.input_df['Number of Months in eClerx'] = self.convert_to_bins(self.input_df['Number of Months in eClerx'], eclerx_tenure_bins)
        eclerx_duration_mapper = {'(-10, 12]': 4, 
                              '(12, 24]': 3, 
                              '(24, 36]': 2, 
                              '(36, 999]': 1}

        self.input_df['Number of Months in eClerx'] = self.input_df['Number of Months in eClerx'].replace(eclerx_duration_mapper)
        categorical_cols = list(self.input_df.select_dtypes(include=['object']).columns) 
        self.input_df[categorical_cols] = self.input_df[categorical_cols].fillna('Blanks')
        
        columns_seq_ss = ['Education Field', 'Is office located in the native state', 'Average daily hours', 
                          'Is Employee under Training Agreement / CEP', 'No. of IJP postings applied', 'Office location', 
                          'No. of unavailed comp offs in last 6 months', 'Loss of Pay in last 6 months', 
                          'unplanned leaves in last 6 months', 'Program', 'Manager Designation', 'Frequency of manager change', 
                          'Number of Months in eClerx', 'Number of Months in Current Designation', 'Designation', 'Awards for the Year', 
                          'Monetory Rewards in last 12 Months', 'Last Year Rating', 'Previous Last Year Rating', 
                          'No. of companies worked', 'Total working years', 'Channel', 'Age', 'Number Of training completed', 
                          'Manager Rating', 'Salary Rank']
        self.input_df = self.input_df[columns_seq_ss]
        return self.input_df

    def co_preprocessor(self):
        if 'Age' not in self.input_df.columns:
            self.input_df['Age'] = 30
        if 'Manager Rating' not in self.input_df.columns:
            self.input_df['Manager Rating'] = 'Blanks'
        if 'Monetory Rewards in last 12 Months' not in self.input_df.columns:
            self.input_df['Monetory Rewards in last 12 Months'] = 0
        if 'Number Of training completed' not in self.input_df.columns:
            self.input_df['Number Of training completed'] = 0
        if 'Previous Last Year Rating' not in self.input_df.columns:
            self.input_df['Previous Last Year Rating'] = 'Blanks'
        if 'unplanned leaves in last 6 months' not in self.input_df.columns:
            self.input_df['unplanned leaves in last 6 months'] = 0
        self.input_df['Age'] = self.input_df['Age'].fillna(30)
        self.input_df['Age'] = self.input_df['Age'].astype('int')
        self.input_df = self.input_df.drop(['No. of IJP postings applied'], axis = 1)
        self.input_df['Average daily hours'] = self.input_df['Average daily hours'].fillna(9.5)
        self.input_df['No. of unavailed comp offs in last 6 months'] = self.input_df['No. of unavailed comp offs in last 6 months'].fillna(0)
        self.input_df['Loss of Pay in last 6 months'] = self.input_df['Loss of Pay in last 6 months'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'] = self.input_df['unplanned leaves in last 6 months'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'][self.input_df['unplanned leaves in last 6 months'] < 0] = 0
        self.input_df['Frequency of manager change'] = self.input_df['Frequency of manager change'].fillna(0)
        self.input_df['Number of Months in eClerx'] = self.input_df['Number of Months in eClerx'].fillna(0)
        self.input_df['Number of Months in eClerx'][self.input_df['Number of Months in eClerx'] < 0] = 0
        self.input_df['Awards for the Year'] = self.input_df['Awards for the Year'].fillna(0)
        self.input_df['Monetory Rewards in last 12 Months'] = self.input_df['Monetory Rewards in last 12 Months'].fillna(0)
        self.input_df = self.input_df.drop(['No. of companies worked'], axis = 1)
        self.input_df['Total working years'] = self.input_df['Total working years'].fillna(0)
        self.input_df['Total working years'][self.input_df['Total working years'] < 0] = 0
        self.input_df['Number Of training completed'] = self.input_df['Number Of training completed'].fillna(0)
        self.input_df = self.input_df.drop(['CCA'], axis = 1)
        self.input_df = self.input_df.drop(['Total working years'], axis = 1)
        tenure_bins = [-10, 12, 24, 36, 999]
        self.input_df['Number of Months in eClerx'] = self.convert_to_bins(self.input_df['Number of Months in eClerx'], tenure_bins)
        eclerx_duration_mapper = {'(-10, 12]': 4, 
                                  '(12, 24]': 3, 
                                  '(24, 36]': 2, 
                                  '(36, 999]': 1}
        self.input_df['Number of Months in eClerx'] = self.input_df['Number of Months in eClerx'].replace(eclerx_duration_mapper)
        categorical_cols = list(self.input_df.select_dtypes(include=['object']).columns)
        self.input_df[categorical_cols] = self.input_df[categorical_cols].fillna('Blank')
        
        columns_seq_co = ['Education Field', 'Is office located in the native state', 'Average daily hours', 
                          'Is Employee under Training Agreement / CEP', 'Office location', 'No. of unavailed comp offs in last 6 months', 
                          'Loss of Pay in last 6 months', 'unplanned leaves in last 6 months', 'Program', 'Manager Designation', 
                          'Frequency of manager change', 'Number of Months in eClerx', 'Number of Months in Current Designation', 
                          'Designation', 'Awards for the Year', 'Monetory Rewards in last 12 Months', 'Last Year Rating', 
                          'Previous Last Year Rating', 'Channel', 'Age', 'Number Of training completed', 'Manager Rating', 'Salary Rank']
        self.input_df = self.input_df[columns_seq_co]
        return self.input_df

    def fm_preprocessor(self):
        if 'Age' not in self.input_df.columns:
            self.input_df['Age'] = 30
        if 'Manager Rating' not in self.input_df.columns:
            self.input_df['Manager Rating'] = 'Blanks'
        if 'Monetory Rewards in last 12 Months' not in self.input_df.columns:
            self.input_df['Monetory Rewards in last 12 Months'] = 0
        if 'Number Of training completed' not in self.input_df.columns:
            self.input_df['Number Of training completed'] = 0
        if 'Previous Last Year Rating' not in self.input_df.columns:
            self.input_df['Previous Last Year Rating'] = 'Blanks'
        if 'unplanned leaves in last 6 months' not in self.input_df.columns:
            self.input_df['unplanned leaves in last 6 months'] = 0
        self.input_df['Age'] = self.input_df['Age'].fillna(30)
        self.input_df['Age'] = self.input_df['Age'].astype('int')
        self.input_df['Average daily hours'] = self.input_df['Average daily hours'].fillna(9.5)
        self.input_df['No. of IJP postings applied'] = self.input_df['No. of IJP postings applied'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'] = self.input_df['unplanned leaves in last 6 months'].fillna(0)
        self.input_df['No. of unavailed comp offs in last 6 months'] = self.input_df['No. of unavailed comp offs in last 6 months'].fillna(0)
        self.input_df = self.input_df.drop(['Is Employee under Training Agreement / CEP'], axis = 1)
        self.input_df['Loss of Pay in last 6 months'] = self.input_df['Loss of Pay in last 6 months'].fillna(0)
        self.input_df['unplanned leaves in last 6 months'][self.input_df['unplanned leaves in last 6 months']<0]=0
        self.input_df['Frequency of manager change'] = self.input_df['Frequency of manager change'].fillna(0)
        self.input_df['Awards for the Year'] = self.input_df['Awards for the Year'].fillna(0)
        self.input_df['Monetory Rewards in last 12 Months'] = self.input_df['Monetory Rewards in last 12 Months'].fillna(0)
        self.input_df['No. of companies worked'] = self.input_df['No. of companies worked'].fillna(0)
        self.input_df['Number Of training completed'] = self.input_df['Number Of training completed'].fillna(0)
        self.input_df=self.input_df.drop(['CCA'],axis=1)
        self.input_df=self.input_df.drop(['Loss of Pay in last 6 months','Frequency of manager change','Total working years'],axis=1)
        eclerx_tenure_bins = [-10, 12, 24, 36, 999]
        self.input_df['Number of Months in eClerx'] = self.convert_to_bins(self.input_df['Number of Months in eClerx'], eclerx_tenure_bins)
        eclerx_duration_mapper = {'(-10, 12]': 4, 
                              '(12, 24]': 3, 
                              '(24, 36]': 2, 
                              '(36, 999]': 1}
        self.input_df['Number of Months in eClerx'] = self.input_df['Number of Months in eClerx'].replace(eclerx_duration_mapper)
        categorical_cols = list(self.input_df.select_dtypes(include=['object']).columns) 
        self.input_df[categorical_cols] = self.input_df[categorical_cols].fillna('Blanks')
        
        columns_seq_fm = ['Education Field', 'Is office located in the native state', 'Average daily hours', 
                          'No. of IJP postings applied', 'Office location', 'No. of unavailed comp offs in last 6 months', 
                          'unplanned leaves in last 6 months', 'Program', 'Manager Designation', 'Number of Months in eClerx', 
                          'Number of Months in Current Designation', 'Designation', 'Awards for the Year', 
                          'Monetory Rewards in last 12 Months', 'Last Year Rating', 'Previous Last Year Rating', 
                          'No. of companies worked', 'Channel', 'Age', 'Number Of training completed', 'Manager Rating', 'Salary Rank']
        self.input_df = self.input_df[columns_seq_fm] 
        return self.input_df


    def handle_newCategories(self):
        # this function will identify the new category if any and replace that category with mode value of the same column
        if self.vertical == 'CO':
            train_df = self.co_train_df.copy()
        if self.vertical == 'FM':
            train_df = self.fm_train_df.copy()
        if self.vertical == 'DI':
            train_df = self.di_train_df.copy()
        if self.vertical == 'SS':
            train_df = self.ss_train_df.copy()
        feature_list = list(self.input_df.select_dtypes(include=['object']).columns)
        for feature in feature_list:
            tr_set = set(list(train_df[feature].value_counts().index))
            te_set = set(list(self.input_df[feature].value_counts().index))
            new_Category_list = list(te_set.difference(tr_set))
            for newVal in new_Category_list:
                if newVal != 'Blank':
                    self.input_df[feature] = self.input_df[feature].replace({newVal : self.input_df[feature].mode()[0]})
        return self.input_df