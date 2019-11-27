# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 15:44:18 2019

@author: aarora33
"""

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

from datetime import datetime
import config_file as cf
import pandas as pd
from Scenario_Manager import ScenarioManager
from Coreference_Resolution import CorefEngine
from Identity_Association import IdentityAssociation
from SEV_Individual_Profile_Screening import ProfileScreening
from Currency_Converter import CurrencyConverter
from Dictionary_Matching import Dictionary_Algo
from CL_DOB_Match import Match_DOB
from nltk.stem.snowball import SnowballStemmer
from itertools import permutations
from fuzzywuzzy import fuzz
import traceback
import time
import warnings
import ast
import numpy as np
warnings.filterwarnings("ignore")

#import spacy
#import numpy as np
#from nltk.stem.snowball import SnowballStemmer
#from pandas import ExcelWriter
#from Dependency_Parser import DependencyParser

def convert_to_dict(list_):
    dic = {}
    if pd.isnull(list_) or (list_) == 0:
        return dic
    list_ = ast.literal_eval(str(list_))
    for i,l in enumerate(list_):
        dic['alias_'+str(i)] = l
    return dic

def CL_countryMatch(row):
    if pd.isnull(row[0]) or pd.isnull(row[1]):
        return None
    try:                
        if (row[0].strip().lower() == row[1].strip().lower()):
            return True             
        else:            
            return False
    except:
        return None        

    #PEP and SOE Scenario:
def check_pep_soe(row):
    subcat = row[0]
    cat = row[1]
    rel_com = row[2]
    rel_ind = row[3]
    if 'PEP' in subcat or 'PEP' in cat or 'PEP' in rel_ind:
        return 1
    elif 'SOE' in subcat or 'SOE' in cat or 'SOE' in rel_com:
        return 1            
    return 0

def check_name_combinations(name_1,name_2,type_flag):
#    print("checking" ,name_1,'----',name_2)
    ratios = []
    if(type_flag == "alias"):
        if  ',' in name_1:
            names = name_1.split(',')            
            for name in names:                
                x = name.split()
#                if len(x) 
                comb = []
                perm = permutations(x)
                for num in perm :
                    comb.append(" ".join(num))
                for c in comb:
    #                print("alias matching-----",name_2,"----",c)
                    ratios.append(fuzz.ratio(name_2,c))
        else:
            #change this logic later
             ratios.append(fuzz.ratio(name_2,name_1))
#        print('alias ratios: ', ratios)
    else:
        x = name_1.split()
        comb = []
        perm = permutations(x)
        for num in perm :
            comb.append(" ".join(num))
        for c in comb:
#            print("name matching-----",name_2,"----",c)
            ratios.append(fuzz.ratio(name_2,c))
#        print('name ratios: ', ratios)
    return max(ratios)    

def check_name_combinations_decorator(func):
    def inner(row, type_):                       
        match_list = []    
        input_name = row[0]
        alias_list = row[1]        
        if not isinstance(alias_list, list):
            alias_list = ast.literal_eval(alias_list)
        if len(alias_list) == 0:
            return False
        for alias in alias_list:                                    
            match = func(input_name, alias, type_)                   
            match_list.append(match)        
        if max(match_list) >= 80:
            return True
        else:
            return False
    return inner

def get_scenario_context(row, da):    
    try:
        amount_dict = row[0]
        cntry_dict = row[1]    
        money_flag = row[2]                
        if money_flag:
            if pd.notnull(amount_dict) and pd.notnull(cntry_dict):
                amount_sent = amount_dict['sentences']
                amount_words = amount_dict['amount_context']        
                cntry_sent = cntry_dict['sentences']
                cntry_words = cntry_dict['sanction_context']
                amount_sent.extend(cntry_sent)
                amount_words.extend(cntry_words)
                mat_score = 0.6
                amount_words = da.get_freq_count(amount_words)        
#                print(amount_words, amount_sent)
                return mat_score, amount_words, amount_sent
            elif pd.notnull(amount_dict):        
                mat_score = 0.3        
                amount_words = da.get_freq_count(amount_dict['amount_context'])
#                print(amount_words, amount_dict['sentences'])
                return mat_score, amount_words, amount_dict['sentences']            
        elif pd.notnull(cntry_dict):
            mat_score = 0.3        
            sanc_words = da.get_freq_count(cntry_dict['sanction_context'])                
#           print(sanc_words, cntry_dict['sentences'])
            return mat_score, sanc_words, cntry_dict['sentences']            
        else:            
            return None, None, None
    except Exception as e:
        print(traceback.format_exc())        
        return None, None, None


#'Material_Score', 'Material Context', 'Amount', 'money_flag'

def get_non_material_reason(row, sev_flag):    
    material_score = row[0]    
    material_context = row[1]
    amount = row[2]
    amount_flag = row[3]
    reason = None
    if sev_flag:
        whitelisted = row[4]
        prof_mismatch_flag = row[5]
    else:
        whitelisted = False
        prof_mismatch_flag = False    
    try:
        if whitelisted:
            reason = 'Entity is Whitelisted'
            return reason        
        if prof_mismatch_flag:
            reason = 'Individual profile mismatched'
        elif (material_score is not None and pd.notnull(material_score) and material_score != 'NA' and material_score > 0 ):           
            if (pd.isnull(material_context) or len(material_context) == 0):
                if pd.notnull(amount) and not amount_flag:
                    reason = 'Fined amount is less than the threshold defined'
                else:
                    reason = 'Absence of material context'                
        else:
            reason = np.nan
        return reason
    except:        
        return reason
    

if '__name__==__main':    
    start_time = time.time()
    print('start time', datetime.now())    
    sanc_file = cf.sanc_file
    fined_scnr_file = cf.fined_scnr_file
    kw_material = Dictionary_Algo().read_file_postag(cf.kw_material)
    kw_neg_ds = Dictionary_Algo().read_file_postag(cf.kw_neg_ds)
    kw_non_neg = Dictionary_Algo().read_file_postag(cf.kw_non_neg)
    kw_negation = Dictionary_Algo().read_file(cf.kw_negation, 'utf-8')    
    job_titles = Dictionary_Algo().read_file(cf.job_titles, 'utf-8-sig')
    cureency_df = pd.read_excel(cf.cureency_df)   
    sanctioned_scenario_words = Dictionary_Algo().read_file(cf.sanctioned_scenario_words, 'utf-8')    
        
    #read SEV and CL input data    
    input_df = pd.read_excel(cf.input_file)    
    input_df['file_name_id'] = input_df['file_name_id'].apply(lambda x : x.replace('_','-'))
    #CL    
    cl_input_df = pd.read_excel(cf.cl_input_file)        
            
    da = Dictionary_Algo()    
    cor_eng = CorefEngine()
    ia = IdentityAssociation()
    sm = ScenarioManager()
    psc = ProfileScreening()        
    cc = CurrencyConverter()
    mdob = Match_DOB()
    
    #convert material post tag word list to wordlist    
    wordList = sm.read_file_postag(cf.kw_material)
    stemmer = SnowballStemmer("english")
    materialWord_list = []
    for word in wordList:
        tempStr = ' '
        tempStr = tempStr.join([i[0] for i in word])
        materialWord_list.append(sm.get_stemming(tempStr, stemmer))    
        
#    loading CL data
    cl_path = cf.cl_txt_files_path
    cl_df = cor_eng.get_cl_data(cl_path)        
    
    stemmer = SnowballStemmer("english")
    stemmed_sanc_word_list = []
    for i in sanctioned_scenario_words:
        stemmed_sanc_word_list.append(sm.get_stemming(i, stemmer))        
        
    currency_db = cc.currency_excel_dataextraction(cureency_df)###the dictonary of all currency codes    
    #------------------------------------------------------------------------------------------------------
    #1.Coref resolution
    df = cor_eng.coref_orchestrator(materialWord_list)       
    if df.shape[0] >  0:
        print('-------------------------Classifying SEV---------------------')            
        #get coreferences
        df['coref'] = df['clean_text_for_coref'].apply(lambda x: cor_eng.get_coref(x))        
        
        df = pd.merge(df, input_df[['file_name_id', 'alias', 'Whitelisted Entity(if any)']], on='file_name_id', how = 'left')
        df['alias_dict'] = df['alias'].apply(convert_to_dict)    
        #2.Identity association    
        df['Entity Relevance Score'], df['Entity Related Text'], df['Entity Coref Text'], df['Entity Presence'] = zip(*df[['coref', 'Entity', 'Article Text', 'alias_dict']].apply(ia.entity_related_text, axis=1))
        
        print('df_IA: ', df.shape)    
        print('Coref and IA end time', datetime.now())    
        print('time taken to process Coref and IA ', (time.time() - start_time)/60) 
        #3.1 Individual SEV Profile Matching            
        check_profile_df = df[df['type'] == 'individual']
        check_entity_df = df[df['type'] == 'entity']
        
        print('entity df and profile df is:', check_entity_df.shape, check_profile_df.shape)
        
        profile_df = pd.DataFrame(columns = check_profile_df.columns)            
        if check_profile_df.shape[0] > 0:
            check_profile_df['Individual Age'], check_profile_df['age_context'] = zip(*check_profile_df[['Entity Coref Text','Entity']].apply(lambda x: psc.get_individual_age(x), axis=1))
            check_profile_df['article_job_title'] = check_profile_df[['Entity Coref Text', 'Entity']].apply(lambda x: psc.get_title(x, job_titles), axis = 1)    
            input_df = input_df[input_df['type'] == 'individual']
            input_df.drop(['type','alias','Whitelisted Entity(if any)'], axis=1, inplace=True)             
            check_profile_df = pd.merge(check_profile_df, input_df, on='file_name_id', how = 'left')
            check_profile_df['mismatch'] = check_profile_df[['age', 'job_title', 'Individual Age','article_job_title']].apply(da.match_individual_profile, axis=1)
    #    print(check_profile_df[['article_job_title', 'job_title', 'mismatch']])
            profile_df = check_profile_df[check_profile_df['mismatch']==True]                    
            false_profile_df = check_profile_df[check_profile_df['mismatch']==False]
            print('profile mismatch df found with size:', profile_df.shape, 'False profile df', false_profile_df.shape)
        
        if profile_df.shape[0] == 0:
            profile_df = pd.DataFrame(columns = check_profile_df.columns)            
            df['mismatch']=False        
        elif profile_df.shape[0] > 0:
            #mismatch false: check_profile_df, merge with check_entity_df        
            check_entity_df['mismatch']=None
            check_entity_df['Individual Age']=None
    #        check_entity_df['Whitelisted Entity(if any)']=None
            check_entity_df['age_context']=None                       
            check_entity_df['article_job_title']=None                       
            check_entity_df['age']=None                       
            check_entity_df['job_title']=None            
            profile_df = profile_df[check_entity_df.columns]
            true_none_profileMatch_df = check_profile_df[check_profile_df['mismatch']==False]
            print('True none df', true_none_profileMatch_df.shape)
            true_none_profileMatch_df = true_none_profileMatch_df[check_entity_df.columns]
            #merge entity and mismatch False/None df
            df = pd.concat([check_entity_df, true_none_profileMatch_df], axis=0, ignore_index=True)    
            print('df after entity and mismatch false is processed', df.shape)
        print('profile screening end time', datetime.now())    
        print('time taken to process profile screening', (time.time() - start_time)/60) 
        
        #3.Money Scenario       
        sm_start_time = time.time()         
        print('----------df', df.shape)
        if df.shape[0] > 0:
            df['money_flag'], df['Amount'] = zip(*df[['Entity Coref Text', 'Entity', 'filename']].apply(lambda x: sm.scenario_manager('money', x, sanc_file, fined_scnr_file, kw_negation, currency_db, stemmed_sanc_word_list), axis=1))
            df['country_flag'], df['Sanction Country'] = zip(*df[['Entity Coref Text', 'Entity','filename']].apply(lambda x: sm.scenario_manager('country', x, sanc_file, fined_scnr_file, kw_negation, currency_db, stemmed_sanc_word_list), axis=1))        
            
            print('scenario manager executed successfully')
            print('scenario manager end time', datetime.now())    
            print('time taken to process scenario manager', (time.time() - sm_start_time)/60) 
            
            #Scenario df
            scenario_df = df[(df['Sanction Country'].notnull()) | (df['money_flag'] == True)]                    
            if scenario_df.shape[0] > 0:        
                #============================================================================
    #            print(scenario_df[['Material_Score', 'Material Context', 'Material/ Severity sentence']].dtypes)
                print('---------')
                scenario_df['Material_Score'], scenario_df['Material Context'], scenario_df['Material/ Severity sentence'] =  zip(*scenario_df[['Amount', 'Sanction Country', 'money_flag']].apply(lambda x: get_scenario_context(x, da), axis=1))
                scenario_df['Amount'] =  scenario_df['Amount'].apply(lambda x: x['money'] if pd.notnull(x) else np.nan)
                scenario_df['Sanction Country'] =  scenario_df['Sanction Country'].apply(lambda x: x['country'] if pd.notnull(x) else np.nan)
            else:
                scenario_df['Material/ Severity sentence'] = None            
            #============================================================================
                
            scenario_df['System Classification'] = 'Material'    
            scenario_df['ndp_words'] = None
            scenario_df['dp_words'] = None        
            scenario_df['Non-material context'] = None                                          
            scenario_df['Severity'] = None            
            print('Scenario DF is', scenario_df.shape)
            profile_df['System Classification'] = 'Non-Material'    
            profile_df['ndp_words'] = None
            profile_df['dp_words'] = None
            profile_df['Sanction Country'] = None                     
            profile_df['Amount'] = None
            profile_df['Material Context'] = None
            profile_df['Non-material context'] = None                                          
            profile_df['Severity'] = None
            profile_df['Material/ Severity sentence'] = None     
            profile_df['Material_Score'] = 0     
            
            print('profile df shape', profile_df.shape)
            scenario_profile_output_df = pd.concat([scenario_df, profile_df], axis=0, ignore_index=True)
            print('scenario_profile_output_df shape is', scenario_profile_output_df.shape)
            timestamp = 'SEV_ScenarioOutput_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
            output_path = os.path.join('../output', timestamp)    
            da.write_excel(scenario_df, output_path)
            print('Scenario file written successfully', output_path)
            #4.Dictionary Matching Algorithm        
            #Scenario Filtered df        
            scenario_filtered_df = df[(df['Sanction Country'].isnull()) & (df['money_flag'] == False)]
            print('--------scenario filtered df is ready!!-------', scenario_filtered_df.shape)
            if scenario_filtered_df.shape[0] > 0:
                print('-----------------------------------------------')
                da_start_time = time.time()
                scenario_filtered_df['Amount'] =  scenario_filtered_df['Amount'].apply(lambda x: x['money'] if pd.notnull(x) else np.nan)
                scenario_filtered_df['Sanction Country'] =  scenario_filtered_df['Sanction Country'].apply(lambda x: x['country'] if pd.notnull(x) else np.nan)            
                #calling dictionary algo
                scenario_filtered_df['ndp_words'], scenario_filtered_df['dp_words'], scenario_filtered_df['Material Context'], scenario_filtered_df['Severity'], scenario_filtered_df['Non-material context'], scenario_filtered_df['Material/ Severity sentence'], scenario_filtered_df['Material_Score'], scenario_filtered_df['System Classification'] = zip(*scenario_filtered_df[['Entity Coref Text', 'Entity', 'filename']].apply(lambda x: Dictionary_Algo().get_class_score_and_output(x, kw_material, kw_neg_ds, kw_non_neg, kw_negation), axis=1))
        #            scenario_filtered_df['ndp_words'], scenario_filtered_df['dp_words'],  scenario_filtered_df['Material Context'], scenario_filtered_df['Material/ Severity sentence'], scenario_filtered_df['Material_Score'], scenario_filtered_df['System Classification'] = zip(*scenario_filtered_df[['Entity Coref Text', 'Entity']].apply(lambda x: Dictionary_Algo().get_class_score_and_output(x, kw_material, kw_neg_ds, kw_non_neg), axis=1))
                print('Dictionary matching executed successfully')
                print('Dictionary matching  end time', datetime.now())    
                print('time taken to process Dictionary matching ', (time.time() - da_start_time)/60) 
                                        
                #5. Writing output
                #Appending scenario_profile_output_df and Scenario Filtered df                        
                output_df = pd.concat([scenario_filtered_df, scenario_profile_output_df], axis=0, ignore_index=True)
                
                # -------Adding reason of non material----------------
    #            change system class if entity is whitelisted            
                output_df.loc[output_df['Whitelisted Entity(if any)']  == True, 'System Classification'] = 'Non-Material'
                output_df['Reason for Non-Material'] = output_df[['Material_Score', 'Material Context', 'Amount', 'money_flag', 'Whitelisted Entity(if any)', 'mismatch']].apply(lambda x: get_non_material_reason(x, True), axis=1)
                
                
                output_df.drop(columns=['clean_text_for_coref', 'coref','alias', 'alias_dict', 'country_flag', 'dp_words', 'file_name_id', 'ndp_words'], inplace = True)
                print('Dataframe appended successfully', output_df.shape, scenario_filtered_df.shape, scenario_df.shape)
                #write file in the output folder for each datetime period
                timestamp = 'SEV_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
                output_path = os.path.join('../output', timestamp)    
                da.write_excel(output_df, output_path)
                print('file written successfully', output_path)
            else:
                scenario_profile_output_df.drop(columns=['clean_text_for_coref', 'coref','alias', 'alias_dict', 'country_flag', 'dp_words', 'file_name_id', 'ndp_words'], inplace = True)
                timestamp = 'SEV_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
                output_path = os.path.join('../output', timestamp)    
                da.write_excel(scenario_profile_output_df, output_path)
                print('file written successfully', output_path)
            print('Sev end time', datetime.now())    
            print('time taken to process Sev ', (time.time() - start_time)/60) 
        else:
            profile_df.drop(columns=['clean_text_for_coref', 'coref','alias', 'alias_dict', 'file_name_id'], inplace = True)
            timestamp = 'SEV_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
            output_path = os.path.join('../output', timestamp)    
            da.write_excel(profile_df, output_path)
            print('file written successfully', output_path)
            print('Sev end time', datetime.now())    
            print('time taken to process Sev ', (time.time() - start_time)/60)         
    #    #        ---------------------------------------------------------------------------------------------
        
    if cl_df.shape[0] > 0:
        print('--------------------------Classifying CL---------------------------')
        cl_start_time = time.time()    
        cl_df['Entity'] = cl_df['File Path'].apply(lambda x: x.split('CL_')[1].split('_')[0])
        cl_df['file_name_id'] = cl_df['File Path'].apply(lambda x: os.path.basename(x)[:os.path.basename(x).rfind('_')])
        cl_df = pd.merge(cl_df, cl_input_df, on='file_name_id', how = 'left')        
        # Alias match logic:
        check_name_dec = check_name_combinations_decorator(check_name_combinations)
        cl_df['alias_flag'] = cl_df[['hit_name', 'input_alias']].apply(lambda x: check_name_dec(x, 'name'), axis=1)
        cl_df.loc[cl_df['alias_flag'] == True, 'hit_status'] = 'true_hit'           
        # input country match
        cl_df['country_match_flag'] = cl_df[['input_country', 'Country']].apply(CL_countryMatch, axis=1)    
        
        cl_df.loc[((cl_df['hit_status'] == 'false_positive') & (cl_df['match_ratio'] >= 50) & (cl_df['Risk'] == 'high')), 'hit_status'] = 'true_hit'    
                  
        # filter only true_hits        
        fp_hits_df = cl_df[cl_df['hit_status'] == 'false_positive']    
        fp_hits_df['age_match_flag'] = np.nan
        fp_hits_df['pass_flag'] = np.nan
        cl_df = cl_df[cl_df['hit_status'] == 'true_hit']    
        
        # match DOB CL        
        
        cl_df['age_match_flag'], cl_df['pass_flag'] = zip(*cl_df[['input_dob', 'DOB_POB']].apply(lambda x: mdob.compareAge(x), axis=1))    
        cl_df.loc[cl_df['pass_flag'] == False, 'hit_status'] = 'false_positive'    
        fp_cl_df = cl_df[cl_df['hit_status'] == 'false_positive']
        cl_df = cl_df[cl_df['hit_status'] == 'true_hit']        
        fp_hits_df = fp_hits_df.append(fp_cl_df)    
        print('FP DF appended after DOB check', fp_cl_df.shape, fp_hits_df.shape)
        
        cl_df['pep_soe'] = cl_df[['Subcategory', 'Category', 'Related_Companies', 'Related_Individuals']].apply(lambda x: check_pep_soe(x), axis=1)
        pep_cl_df = cl_df[cl_df['pep_soe']==1]    
        pep_cl_df['Material Context'] = "{'pep/soe': 1}"
        cl_df = cl_df[cl_df['pep_soe']==0]     
        
        #3.Money Scenario  
        if cl_df.shape[0] > 0:
            cl_df['money_flag'], cl_df['Amount'] = zip(*cl_df[['Article Text', 'Entity', 'File Path']].apply(lambda x: sm.scenario_manager('money', x, sanc_file, fined_scnr_file, kw_negation, currency_db, stemmed_sanc_word_list), axis=1))
            cl_df['country_flag'], cl_df['Sanction Country'] = zip(*cl_df[['Article Text', 'Entity', 'File Path']].apply(lambda x: sm.scenario_manager('country', x, sanc_file, fined_scnr_file, kw_negation, currency_db, stemmed_sanc_word_list), axis=1))        
            print('scenario manager executed successfully')
            #Scenario df                     
            scenario_cl_df = cl_df[cl_df['Sanction Country'].notnull() | cl_df['money_flag'] == True]
            if scenario_cl_df.shape[0] > 0:        
                #============================================================================
                scenario_cl_df['Material_Score'], scenario_cl_df['Material Context'], scenario_cl_df['Material/ Severity sentence'] =  zip(*scenario_cl_df[['Amount', 'Sanction Country', 'money_flag']].apply(lambda x: get_scenario_context(x, da), axis=1))
                scenario_cl_df['Amount'] =  scenario_cl_df['Amount'].apply(lambda x: x['money'] if pd.notnull(x) else np.nan)
                scenario_cl_df['Sanction Country'] =  scenario_cl_df['Sanction Country'].apply(lambda x: x['country'] if pd.notnull(x) else np.nan)
            else:
                scenario_cl_df['Material/ Severity sentence'] = None    
                           
            scenario_cl_df['System Classification'] = 'Material'    
            scenario_cl_df['ndp_words'] = None
            scenario_cl_df['dp_words'] = None                
            pep_cl_df['System Classification'] = 'Material'    
            pep_cl_df['ndp_words'] = None
            pep_cl_df['dp_words'] = None
            pep_cl_df['Sanction Country'] = None                     
            pep_cl_df['Amount'] = None        
            pep_cl_df['Non-material context'] = None                                          
            pep_cl_df['Severity'] = None
            pep_cl_df['Material/ Severity sentence'] = None        
            pep_cl_df['Material_Score'] = 0.4
            
            fp_hits_df['System Classification'] = 'False Positive Entity'        
            scenario_pep_cl_df = pd.concat([scenario_cl_df, pep_cl_df], axis=0, ignore_index=True)            
            fp_scenario_pep_cl_df = pd.concat([scenario_pep_cl_df, fp_hits_df], axis=0, ignore_index=True)            
            #4.Dictionary Matching Algorithm        
            #Scenario Filtered df    
            scenario_filtered_cl_df = cl_df[cl_df['Sanction Country'].isnull() & cl_df['money_flag'] == False]
            print('--------scenario filtered df is ready!!-------', scenario_filtered_cl_df.shape)
            
            if scenario_filtered_cl_df.shape[0] > 0:
                scenario_filtered_cl_df['Amount'] =  scenario_filtered_cl_df['Amount'].apply(lambda x: x['money'] if pd.notnull(x) else np.nan)
                scenario_filtered_cl_df['Sanction Country'] =  scenario_filtered_cl_df['Sanction Country'].apply(lambda x: x['country'] if pd.notnull(x) else np.nan)
                scenario_filtered_cl_df['ndp_words'], scenario_filtered_cl_df['dp_words'],scenario_filtered_cl_df['Material Context'], scenario_filtered_cl_df['Severity'], scenario_filtered_cl_df['Non-material context'], scenario_filtered_cl_df['Material/ Severity sentence'],scenario_filtered_cl_df['Material_Score'], scenario_filtered_cl_df['System Classification'] = zip(*scenario_filtered_cl_df[['Article Text', 'Entity', 'File Path']].apply(lambda x: Dictionary_Algo().get_class_score_and_output(x, kw_material, kw_neg_ds, kw_non_neg, kw_negation), axis=1))    
                print('Dictionary matching executed successfully')
                #5. Writing output
                #Appending pep, scenario df and Scenario Filtered df                            
                output_cl_df = pd.concat([scenario_filtered_cl_df, fp_scenario_pep_cl_df], axis=0, ignore_index=True)        
                print('Dataframe appended successfully', output_cl_df.shape, scenario_filtered_cl_df.shape, scenario_cl_df.shape)
                
                
                output_cl_df['Reason for Non-Material'] = output_cl_df[['Material_Score', 'Material Context', 'Amount', 'money_flag']].apply(lambda x: get_non_material_reason(x, False), axis=1)
                            
                #write file in the output folder for each datetime period
                output_cl_df.drop(columns=['alias_flag', 'country_flag', 'dp_words', 'file_name_id', 'ndp_words', 'pass_flag'], inplace = True)
                timestamp = 'CL_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
                output_path = os.path.join('../output', timestamp)    
                da.write_excel(output_cl_df, output_path)
                print('file written successfully', output_path)
            else:
                fp_scenario_pep_cl_df.drop(columns=['alias_flag', 'country_flag', 'dp_words', 'file_name_id', 'ndp_words', 'pass_flag'], inplace = True)
                timestamp = 'CL_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
                output_path = os.path.join('../output', timestamp)    
                da.write_excel(fp_scenario_pep_cl_df, output_path)                
                print('file written successfully', output_path)
            print('CL end time', datetime.now())    
            print('time taken to process CL ', (time.time() - cl_start_time)/60) 
        else:
            concat_pep_cl_df = pd.concat([fp_hits_df, pep_cl_df], axis=0, ignore_index=True)            
            concat_pep_cl_df.drop(columns=['alias_flag', 'file_name_id', 'pass_flag'], inplace = True)
            timestamp = 'CL_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
            output_path = os.path.join('../output', timestamp)    
            da.write_excel(concat_pep_cl_df, output_path)
            print('file written successfully', output_path)

