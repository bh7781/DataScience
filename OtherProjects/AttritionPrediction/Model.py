import pandas as pd
import joblib
import eli5
import numpy as np
from xgboost import XGBClassifier
from sklearn import metrics

class Model():
    
    def __init__(self, vertical, train_df, test_df):
        self.vertical = vertical
        self.train_df = train_df
        self.test_df = test_df
        self.X_test = self.test_df.loc[:, test_df.columns != 'Is_active']
    
    def train_test_splitting(train_df, test_df):
        x_train = train_df.loc[:, train_df.columns != 'Is_active']
        y_train = train_df.Is_active

        x_test = test_df.loc[:, test_df.columns != 'Is_active']
        y_test = test_df.Is_active

        return x_train, y_train, x_test, y_test

    def XGBoost_model(vertical_str, x_tr, y_tr, x_te, y_te):

        if vertical_str == 'DI':
            xgbc = XGBClassifier(colsample_bytree= 0.8, learning_rate= 0.1, max_depth= 7, n_estimators= 100, n_jobs= 4, 
                             objective= 'binary:logistic', seed= 27, subsample= 0.7)
        
        if vertical_str == 'FM':
            xgbc = XGBClassifier(colsample_bytree= 0.7, learning_rate= 0.05, max_depth= 6, n_estimators= 500, n_jobs= 4, 
                             objective= 'binary:logistic', seed= 27, subsample= 0.8)
    
        if vertical_str == 'CO':
            xgbc = XGBClassifier(colsample_bytree= 0.7, learning_rate= 0.01, max_depth= 7, n_estimators= 750, n_jobs= 4, 
                             objective= 'binary:logistic', seed= 27, subsample= 0.8)
        
        if vertical_str == 'SS':
            xgbc = XGBClassifier(colsample_bytree= 0.7, learning_rate= 0.1, max_depth= 6, n_estimators= 100, n_jobs= 4, 
                             objective= 'binary:logistic', seed= 27, subsample= 0.7)
        
        xgbc.fit(x_tr, y_tr)

        xgb_predictions = xgbc.predict(x_te)
        probabilities_arr = xgbc.predict_proba(x_te)

        prob_df = pd.DataFrame(probabilities_arr, columns=['Attrition_prob', 'No_Attrition_prob'])
        report = metrics.classification_report(y_te, xgb_predictions)

        print(report)
        print(metrics.confusion_matrix(y_te, xgb_predictions))

        # plot_importance(xgbc, height=0.5, grid=False, importance_type='gain')
        # plt.show()
        pickle_path = r'C:\Users\chinmay.shelke\Downloads\Projects\AttritionPrediction\NewCode\Final_v1\pickles\\'
        joblib.dump(xgbc, open(pickle_path + str(vertical_str) + '_xgboost.joblib', 'wb'))

        return xgbc, xgb_predictions, x_te, prob_df

    def predict_attrition(self):
        pickle_path = r'C:\Users\chinmay.shelke\Downloads\Projects\AttritionPrediction\NewCode\Final_v1\pickles\\'
        xgboost_pickle = joblib.load(open(pickle_path + str(self.vertical) + '_xgboost.joblib', 'rb'))
        xgb_predictions = xgboost_pickle.predict(self.X_test)
        probabilities_arr = xgboost_pickle.predict_proba(self.X_test)
        prob_df = pd.DataFrame(probabilities_arr, columns=['Attrition_prob', 'No_Attrition_prob'])
        return xgboost_pickle, xgb_predictions, prob_df


    def explainprediction(self, model_object, prediction_array, probability_dataframe):
        featuresname = list(self.X_test.columns)
        columnsname = [x for x in featuresname]
        # weightobj = eli5.explain_weights_xgboost(model_object, top=None, feature_names=list(featuresname), 
        #                                          importance_type='gain')

        # elw = eli5.format_as_dataframe(weightobj)
        outputdf = pd.DataFrame(columns=columnsname)
        for i in range(self.X_test.shape[0]):
            predobj = eli5.explain_prediction_xgboost(model_object, self.X_test.iloc[i], vec=None, top=None, 
                                                      top_targets=None, target_names=None, targets=None, 
                                                      feature_names=list(featuresname))
            el = eli5.format_as_dataframe(predobj)
            activefeature = list(el['feature'])
            y_pred_temp = np.array([str(x) for x in prediction_array])
            y_pred_temp = list(y_pred_temp)
            #print(el.shape)
            for k in range(el.shape[0]):
                outputdf.loc[i,activefeature[k]] = el.loc[k,'weight']
                outputdf.loc[i,'Prediction'] = y_pred_temp[i]

        outputdf['Attrition_prob'] = probability_dataframe["Attrition_prob"]
        outputdf['No_Attrition_prob'] = probability_dataframe["No_Attrition_prob"] 
        # outputdf["Unique_ID"] = self.X_test.index
        outputdf = outputdf.fillna(value = 0)
        return outputdf