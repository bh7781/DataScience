# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 12:33:58 2018

@author: aarora33
"""
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
from datetime import datetime
from itertools import chain
import spacy
import pandas as pd
from nltk.stem.snowball import SnowballStemmer
from Scenario_Manager import ScenarioManager
from pandas import ExcelWriter
from Coreference_Resolution import CorefEngine
from Identity_Association import IdentityAssociation
from Dependency_Parser import DependencyParser
from SEV_Individual_Profile_Screening import ProfileScreening
from Currency_Converter import CurrencyConverter
import numpy as np
import collections
import traceback
import ast


class Dictionary_Algo(ScenarioManager): 
    
    def __init__(self):
        self.stemmer = SnowballStemmer("english")
        self.nlp = spacy.load('en_coref_sm')
        self.dp = DependencyParser()
        self.ia = IdentityAssociation()
    
    def get_freq_count(self, list_):
        list_ = list(chain.from_iterable(list_))
        dict_ = dict(collections.Counter(list_))
        if len(dict_) > 0:
            return dict_
        else:
            return {}
    
    def write_excel(self,df, path):
        writer = ExcelWriter(path)
        df.to_excel(writer,'Sheet1', index = False)
        writer.save()
    
    def get_classification(self, stemmer, sentence, kw_material, kw_neg_ds, kw_non_neg, entity, kw_negation):        
        #calculate M, PM, and NM
        flag = False
        status = None
        ndp, dp, mtrl_words, flag = self.is_word_tag_match(kw_material, sentence, stemmer, entity, kw_negation, 2)        
        if (flag):        
            #write non-negative near by words logic
            status = 'M'
            return ndp, dp, mtrl_words, status
        elif flag == False:        
            ndp, dp, ds_neg_words, flag = self.is_word_tag_match(kw_neg_ds, sentence, stemmer, entity, kw_negation, -1)                    
            if (flag):
                #write non-negative near by words logic
                ndp, dp, non_neg_words, flag_nn = self.is_word_tag_match(kw_non_neg, sentence, stemmer, entity, kw_negation, 2)                    
                if(flag_nn):
                    status = 'NM'
                    return ndp, dp, non_neg_words, status
                else:                
                    status = 'PM'
                    return ndp, dp, ds_neg_words, status
            else:
                status = 'NM'
                return ndp, dp, [], status
            
    def get_class_score_and_output(self, text_entity, kw_material, kw_neg_ds, kw_non_neg, kw_negation):
        m_count = 0; nm_count = 0; pm_count = 0
        m_list = []; nm_list = []; pm_list = []; ndp_list = []; dp_list = []
        cal_class = None
        mat_score = None
        sentences_list = []        
        try:
            print('Running computations for file:', text_entity[2])            
            text = text_entity[0]
            entity = text_entity[1].strip()                        
            try:
                text = text.to_string(header=False, index=False)    
            except:
                text = str(text)               
            if len(text) == 0 or text.strip() == '':
                mat_score = 'NA'                
                cal_class = 'Entity not found'       
                return ndp_list, dp_list, m_list, pm_list, nm_list, sentences_list, mat_score, cal_class
            
            doc = self.nlp(text)        
            total_sentences = len(list(doc.sents))                
            for i in doc.sents:    
                ndp, dp, words,status = self.get_classification(self.stemmer, str(i), kw_material, kw_neg_ds, kw_non_neg, entity, kw_negation)                
                if len(ndp) > 0:
                    ndp_list.append(ndp)
                if len(dp) > 0:
                    dp_list.append(dp)
                if status == 'M':
                    m_count += 1
                    m_list.append(words)                
                    sentences_list.append(str(i))
                elif status == 'PM':
                    pm_count += 1
                    pm_list.append(words)
                    sentences_list.append(str(i))
                elif status == 'NM':                    
                    if len(words) > 0 and words != None:
                        nm_list.append(words)            
                        sentences_list.append(str(i))    
                    nm_count += 1                
                    
    #        print('total_sentences------------: ', total_sentences)
            if(total_sentences) > 0:            
                mat_per = round(m_count/total_sentences,2)
                par_mat_per = round(pm_count/total_sentences,2)        
                if mat_per > 0:
                    cal_class = 'Material'     
                    mat_score = 0.4                    
                elif par_mat_per >  0:
                    cal_class = 'Non-Material'            
                    mat_score = 0.1 
                else:
                    cal_class = 'Non-Material'
                    mat_score = 0
            else:
                mat_per = 'NA'
                par_mat_per = 'NA'                
                mat_score = 'NA'
                
                cal_class = 'Entity not found'       
#            m_list = [val for sublist in m_list for val in sublist]            
#            pm_list = [val for sublist in pm_list for val in sublist]
#            nm_list = [val for sublist in nm_list for val in sublist]      
            m_list = self.get_freq_count(m_list)
            pm_list = self.get_freq_count(pm_list)
            nm_list = self.get_freq_count(nm_list)            
            ndp_list = list(chain.from_iterable(ndp_list))                  
            dp_list = list(chain.from_iterable(dp_list))                                                              
            return ndp_list, dp_list, m_list, pm_list, nm_list, sentences_list, mat_score, cal_class                        
        except Exception as e:
            print('error in Dictionary algo', str(e))
            print(traceback.format_exc())
            cal_class = 'Error in processing'        
            ndp_list = list(chain.from_iterable(ndp_list))                              
            dp_list = list(chain.from_iterable(dp_list))                     
            return ndp_list, dp_list, m_list, pm_list, nm_list, sentences_list, mat_score, cal_class
    
    def match_individual_profile(self, io_data):
        age = io_data[0]
        job = io_data[1]        
        article_age = io_data[2]
        article_job = io_data[3]      
        flag = False                  
        try:                 
            job = ast.literal_eval(str(job))
            job = [i.lower() for i in job]  
            if pd.notnull(age) and article_age != None:
                if (int(age) != int(article_age)):
                    flag = True
            elif len(job) > 0 and article_job != None:
                if article_job.lower().strip() not in ' '.join(job):
                    # ideally flag should be true, but keeping it false as sometime job title extraction 
                    #accuracy is low and it get's falsely classified as non-material
                    flag = False             
            else:                
                flag = False
        except Exception as e:
            print('error in Profile screening', job)
            print(traceback.format_exc())
            flag = False
        return flag
        #return mismatch = true, when profile mismatch is there.
        
        

#if '__name__==__main':
#    sanc_file = '../corpus/sanctioned_countries.txt'
#    fined_scnr_file = '../corpus/fine_scenario_words.txt'
#    kw_material = Dictionary_Algo().read_file_postag('../corpus/Material.txt')
#    kw_neg_ds = Dictionary_Algo().read_file_postag('../corpus/Negative_domain_specific.txt')
#    kw_non_neg = Dictionary_Algo(). read_file_postag('../corpus/non_negative.txt')
#    kw_negation = Dictionary_Algo(). read_file('../corpus/Negations.txt', 'utf-8')    
#    job_titles = Dictionary_Algo(). read_file('../corpus/job_titles_new.txt', 'utf-8-sig')
#    cureency_df = pd.read_excel('../corpus/curency_data_unique.xlsx') ##data extraction from excel    
#    
#    da = Dictionary_Algo()    
#    cor_eng = CorefEngine()
#    ia = IdentityAssociation()
#    sm = ScenarioManager()
#    psc = ProfileScreening()        
#    cc = CurrencyConverter()
#    
#    currency_db = cc.currency_excel_dataextraction(cureency_df)###the dictonary of all currency codes
#    # change flags accoridng to which type of data to be used in NLP engine
#    sev_flag = True
#    individual_flag = True
#    
#    if sev_flag:               
#        print('-------------------------Classifying SEV---------------------')
#        #1.Coref resolution
#        df = cor_eng.coref_orchestrator()
#        #get coreferences
#        df['coref'] = df['clean_text_for_coref'].apply(lambda x: cor_eng.get_coref(x))
#        #2.Identity association
#        df['entity_relevance_score'], df['entity_raw_text'], df['entity_text'], df['entity_found'] = zip(*df[['coref', 'entity', 'raw_text']].apply(ia.entity_related_text, axis=1))
#        print('df_IA: ', df.shape)
#        
#        #3.1 Individual SEV Profile Matching        
#        if individual_flag:
#            df['article_individual_age'], df['age_context'] = zip(*df[['entity_text','entity']].apply(lambda x: psc.get_individual_age(x), axis=1))
#            df['article_job_title'] = df[['entity_text', 'entity']].apply(lambda x: psc.get_title(x, job_titles), axis = 1)
#            #read input data
#            input_file = r'../data/input_data/profile_input.xlsx'
#            input_df = pd.read_excel(input_file)
#            df = pd.merge(df, input_df, on='file_name_id', how = 'left')
#            # write a function which will match age and job title from OPS inputs
#            df['mismatch'] = df[['age', 'job_title', 'article_individual_age','article_job_title']].apply(da.match_individual_profile, axis=1)
#            profile_df = df[df['mismatch']==True]
#            print('profile mismatch df found with size:', profile_df.shape)            
#        else:
#            profile_df = pd.DataFrame(columns = df.columns)            
#            df['mismatch']=False
#        #3.Money Scenario        
#        if df.shape[0] > profile_df.shape[0]:
#            df = df[df['mismatch']==False]
#            df['amount_verification'] = df[['entity_text', 'entity', 'filename']].apply(lambda x: sm.scenario_manager('money', x, sanc_file, fined_scnr_file, kw_negation, currency_db), axis=1)
#            df['sanction_country_verification'] = df[['raw_text', 'entity','filename']].apply(lambda x: sm.scenario_manager('country', x, sanc_file, fined_scnr_file, kw_negation, currency_db), axis=1)    
#            print('scenario manager executed successfully')
#            #Scenario df
#            scenario_df = df[df['sanction_country_verification'].notnull() | df['amount_verification'].notnull()]            
#            timestamp = 'SEV_ScenarioOutput_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
#            output_path = os.path.join('../output', timestamp)    
#            da.write_excel(scenario_df, output_path)
#            print('Scenario file written successfully', output_path)
#            #4.Dictionary Matching Algorithm        
#            #Scenario Filtered df    
#            scenario_filtered_df = df[df['sanction_country_verification'].isnull() & df['amount_verification'].isnull()]
#            print('--------scenario filtered df is ready!!-------', scenario_filtered_df.shape)
#            if scenario_filtered_df.shape[0] > 0:
#                print('-----------------------------------------------')
#                scenario_filtered_df['ndp_words'], scenario_filtered_df['dp_words'], scenario_filtered_df['material_words'], scenario_filtered_df['negative_words'], scenario_filtered_df['non-negative_words'], scenario_filtered_df['severe_sentences'], scenario_filtered_df['material_score'], scenario_filtered_df['calculated_class'] = zip(*scenario_filtered_df[['entity_text', 'entity', 'filename']].apply(lambda x: Dictionary_Algo().get_class_score_and_output(x, kw_material, kw_neg_ds, kw_non_neg, kw_negation), axis=1))
#    #            scenario_filtered_df['ndp_words'], scenario_filtered_df['dp_words'],  scenario_filtered_df['material_words'], scenario_filtered_df['severe_sentences'], scenario_filtered_df['material_score'], scenario_filtered_df['calculated_class'] = zip(*scenario_filtered_df[['entity_text', 'entity']].apply(lambda x: Dictionary_Algo().get_class_score_and_output(x, kw_material, kw_neg_ds, kw_non_neg), axis=1))
#                print('Dictionary matching executed successfully')
#                #5. Writing output
#                #Appending scenario df and Scenario Filtered df
#                scenario_df['calculated_class'] = 'Material'    
#                scenario_df['ndp_words'] = 'none' 
#                scenario_df['dp_words'] = 'none'
#                        
#                profile_df['calculated_class'] = 'Non-Material'    
#                profile_df['ndp_words'] = None
#                profile_df['dp_words'] = None
#                profile_df['sanction_country_verification'] = None                     
#                profile_df['amount_verification'] = None
#                profile_df['material_words'] = None
#                profile_df['non-negative_words'] = None                                          
#                profile_df['negative_words'] = None
#                profile_df['severe_sentences'] = None
#                profile_df['material_score'] = None
#                
#                temp_output_df = pd.concat([scenario_df, profile_df], axis=0, ignore_index=True)
#                output_df = pd.concat([scenario_filtered_df, temp_output_df], axis=0, ignore_index=True)
#                output_df.drop(columns=['clean_text_for_coref', 'coref'], inplace = True)
#                print('Dataframe appended successfully', output_df.shape, scenario_filtered_df.shape, scenario_df.shape)
#                #write file in the output folder for each datetime period
#                timestamp = 'SEV_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
#                output_path = os.path.join('../output', timestamp)    
#                da.write_excel(output_df, output_path)
#                print('file written successfully', output_path)
#            else:
#                timestamp = 'SEV_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
#                output_path = os.path.join('../output', timestamp)    
#                da.write_excel(scenario_df, output_path)
#                print('file written successfully', output_path)
#        else:
#            timestamp = 'SEV_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
#            output_path = os.path.join('../output', timestamp)    
#            da.write_excel(profile_df, output_path)
#            print('file written successfully', output_path)
#        
#    else:
#        print('--------------------------Classifying CL---------------------------')
#        cl_path = r'../data/pdf_data/cl/pdf_to_text'
#        cl_df = cor_eng.get_cl_data(cl_path)        
#        cl_df['entity'] = cl_df['File Path'].apply(lambda x: x.split('CL_')[1].split('_')[0])
#        print('CL data loaded: ', cl_df.shape)
#        
#        #PEP Scenario:
#        cl_df['pep'] = cl_df['Subcategory'].apply(lambda x: 1 if ('pep' in x.lower()) else 0)
#        pep_cl_df = cl_df[cl_df['pep']==1]
#        cl_df = cl_df[cl_df['pep']==0]
#        #3.Money Scenario        
#        cl_df['amount_verification'] = cl_df[['raw_text', 'entity']].apply(lambda x: sm.scenario_manager('money', x, sanc_file, fined_scnr_file, kw_negation, currency_db), axis=1)
#        cl_df['sanction_country_verification'] = cl_df[['raw_text', 'entity']].apply(lambda x: sm.scenario_manager('country', x, sanc_file, fined_scnr_file, kw_negation, currency_db), axis=1)    
#        print('scenario manager executed successfully')
#        #Scenario df
#        scenario_cl_df = cl_df[cl_df['sanction_country_verification'].notnull() | cl_df['amount_verification'].notnull()]
#        
#        #4.Dictionary Matching Algorithm        
#        #Scenario Filtered df    
#        scenario_filtered_cl_df = cl_df[cl_df['sanction_country_verification'].isnull() & cl_df['amount_verification'].isnull()]
#        print('--------scenario filtered df is ready!!-------', scenario_filtered_cl_df.shape)
#        
#        if scenario_filtered_cl_df.shape[0] > 0:
#            scenario_filtered_cl_df['ndp_words'], scenario_filtered_cl_df['dp_words'],scenario_filtered_cl_df['material_words'], scenario_filtered_cl_df['negative_words'], scenario_filtered_cl_df['non-negative_words'], scenario_filtered_cl_df['severe_sentences'],scenario_filtered_cl_df['material_score'], scenario_filtered_cl_df['calculated_class'] = zip(*scenario_filtered_cl_df[['raw_text', 'entity']].apply(lambda x: Dictionary_Algo().get_class_score_and_output(x, kw_material, kw_neg_ds, kw_non_neg, kw_negation), axis=1))    
#            print('Dictionary matching executed successfully')
#            #5. Writing output
#            #Appending pep, scenario df and Scenario Filtered df
#            scenario_cl_df['calculated_class'] = 'Material'    
#            scenario_cl_df['ndp_words'] = None
#            scenario_cl_df['dp_words'] = None            
#            pep_cl_df['calculated_class'] = 'Material'    
#            pep_cl_df['ndp_words'] = None
#            pep_cl_df['dp_words'] = None
#            pep_cl_df['sanction_country_verification'] = None                     
#            pep_cl_df['amount_verification'] = None
#            pep_cl_df['material_words'] = None
#            pep_cl_df['non-negative_words'] = None                                          
#            pep_cl_df['negative_words'] = None
#            pep_cl_df['severe_sentences'] = None
#            pep_cl_df['material_score'] = None
#                        
#            output_df = pd.concat([scenario_filtered_cl_df, scenario_cl_df], axis=0, ignore_index=True)
#            output_df = pd.concat([output_df, pep_cl_df], axis=0, ignore_index=True)            
#            print('Dataframe appended successfully', output_df.shape, scenario_filtered_cl_df.shape, scenario_cl_df.shape)
#            #write file in the output folder for each datetime period
#            timestamp = 'CL_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
#            output_path = os.path.join('../output', timestamp)    
#            da.write_excel(output_df, output_path)
#            print('file written successfully', output_path)
#        else:
#            timestamp = 'CL_output_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.xlsx'
#            output_path = os.path.join('../output', timestamp)    
#            da.write_excel(scenario_df, output_path)
#            print('file written successfully', output_path)

