# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 20:47:43 2019

@author: chinmay.shelke
"""
from Processor import Processor
from Model import Model
from Label_Encoder import Label_Encoder

import pandas as pd


#json_df = {"Employee Id":122304,"Employee Code":26233,"Employee Name":"Satish Pathak","Joing Date":1488844800000,
#           "Gender":"M","Marital Status":"M","Highest Qualification":"B.E","Education Field":"Technical",
#           "Is office located in the native state":"Y","Last Working Day":"","Is_active":1,"Employee Status":"Confirmed",
#           "Birth Date":254620800000,"Average daily hours":8.0,"Is Employee under Training Agreement \\/ CEP":"No",
#           "No. of IJP postings applied":"","Time to Commute to Office":"","Office location":"Mumbai",
#           "No. of unavailed comp offs in last 6 months":"","Loss of Pay in last 6 months":"",
#           "unplanned leaves in last 6 months":0.0,"Number of Months in the Current Process":0,"Vertical":"Shared Services",
#           "Program":"KM Core","Manager":"Mehul Sadvilkar","Manager Designation":"Associate Program Manager",
#           "Frequency of manager change":"","Number of Months in eClerx":28,"Number of Months in Current Designation":29,
#           "Designation":"Senior Process Manager","Job Role id":"","Awards for the Year":"",
#           "Monetory Rewards in last 12 Months":"","Last Year Rating":"","Previous Last Year Rating":"",
#           "No. of companies worked":"","Total working years":"","Channel of hiring/Hiring type":"","Channel":"",
#           "Source":"","Recruitment agency":"","Age":41,"Number Of training completed":"","Manager Rating":"",
#           "Salary Rank":"Rank 2","CCA":1.0,"BLI Process":"","vcrSubFunction":"","vcrFunction":""}
def attrition_prediction(json_df):
    
    vertical_str = json_df.loc[0, 'Vertical']
    vertical_str = vertical_str.lower()
    
    vertical_dict = {'digital' : 'DI', 
                     'customer operations' : 'CO',
                     'financial markets' : 'FM',
                     'shared services' : 'SS'}
    
    preprocessor = Processor(json_df, vertical_dict[vertical_str])
    print('Before preprocessing.')
    test_samples = preprocessor.combined_preprocessor()
    test_samples = preprocessor.vertical_preprocessor()
    test_samples = preprocessor.handle_newCategories()
    le = Label_Encoder(vertical_dict[vertical_str], pd.DataFrame(), test_samples)
    test_samples = le.labelEncoderTest()
   
    xgb = Model(vertical_dict[vertical_str], pd.DataFrame(), test_samples)
    modelObj, prediction_array, probability_df = xgb.predict_attrition()
    eli5_df = xgb.explainprediction(modelObj, prediction_array, probability_df)
    eli5_df = eli5_df.drop('<BIAS>', axis = 1)
    
    for col in eli5_df.columns:
        eli5_df.rename(columns = {col : 'FI_' + col},inplace=True)
    
    final_result_df = pd.concat([json_df, eli5_df], axis=1)
    
    return final_result_df