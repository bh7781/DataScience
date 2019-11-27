# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 15:38:27 2018

@author: aarora33
"""
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

import spacy
import re
import pandas as pd
from utility_functions import Utility
import json
import time
start_time = time.time()


class CorefEngine(object):
    
    def __init__(self):
        self.nlp = spacy.load('en_coref_sm')   
        self.util = Utility()
        
    def get_data(self, path):    
        data_list = []
        for files in os.listdir(path):             
            with open( os.path.join(path, files), 'r') as f:
                data = json.load(f)
            data['filename'] = files    
            data_list.append(data)
        return data_list
    
    def get_cl_data(self, path):        
        df = pd.DataFrame()
        for files in os.listdir(path):                         
            with open( os.path.join(path, files), 'r') as f:
                data = f.readlines()        
            dic = json.loads(data[0])
            for k,v in dic.items():
                if isinstance(v, int):
                    dic[k] = [v]                    
                else:
                    dic[k] = [v.strip()]
            temp_df = pd.DataFrame.from_dict(dic) 
            df = df.append(temp_df)
        df = df.reset_index(drop=True) 
        df.rename(columns={'Further Information':'Article Text'}, inplace=True)
        return df

    def get_df_from_dict(self, data_dict):
        df = pd.DataFrame(data_dict)        
        return df
    
    def clean_brackets_text(self, text, materialWord_list):
        try:
            bracket_phrases = re.findall("([\(\{\[].*?[\)\]\}])", text)
            if len(bracket_phrases) > 0:    
                for i in bracket_phrases:                
                    word_match = False
                    new_i = re.sub(r"[\(\)\[\]\{\}]", '', i)                
                    words, word_match = self.util.is_word_match(str(new_i), materialWord_list)                
                    if word_match:
                        text = text.replace(i, new_i)                   
                    else:                      
                        text = text.replace(i, '')
            return text
        except:
            text = re.sub("([\(\{\[]).*?([\)\]\}])", "", text)
            return text
        
    def clean_for_coref(self, text, materialWord_list):
#        text = re.sub("([\(\{\[]).*?([\)\]\}])", "", text)
        text = self.clean_brackets_text(text, materialWord_list)
        text = text.replace('\n', ' ').replace('Rs.', 'Rs').split()
        texts = [str(x.strip()) for x in text]          
        return ' '.join(texts)
    
    #coref resolution function from package
    def get_resolved(self, doc, clusters):
        resolved = list(tok.text_with_ws for tok in doc) 
        for cluster in clusters: 
            for coref in cluster: 
                if coref != cluster.main: 
                    resolved[coref.start] = cluster.main.text + doc[coref.end-1].whitespace_ 
                    for i in range(coref.start+1, coref.end): 
                        resolved[i] = "" 
        return ''.join(resolved) 
        
    #get coref function
    def get_coref(self, text):
        doc = self.nlp(text)
        if(doc._.has_coref):
            doc._.coref_clusters
            ent_list = [(X.text, X.label_) for X in doc.ents if X.label_ == 'GPE' or X.label_ == 'ORG' or X.label_ == 'PERSON']
            for i in doc._.coref_clusters:    
                i_str = list(map(str, i))
                for ent in ent_list:          
                    for ind, val in enumerate(i_str):                    
                        if str(ent[0]) in val:                                                                                                            
                            del i_str[ind]                        
                            del i.mentions[ind]
            clusters = doc._.coref_clusters
            doc._.set('coref_resolved', self.get_resolved(doc, clusters))    
            return doc._.coref_resolved
        else:
            return text
        
    def get_date(self, text):
        try:
            text = text[0:50]
            res = re.match('ATC-\d{6,7} - (?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday).*(?:,|-|/|\s)\s*(\d{4})', text, re.I)
            res = res.group(0)
            art_date = re.sub('ATC-\d{6,7}\s*-','',res).strip()
            return art_date
        except:
            return None
        
    def coref_orchestrator(self, materialWord_list):        
        text_data_path = r'../data_new/text/sev'
        m_data = self.get_data(text_data_path)   
        df = self.get_df_from_dict(m_data)
        print('data loaded successfully!!!!!!!!!!!!!')        
        if df.shape[0] > 0:
            #rename cols
            df.rename(columns={'article':'Article Text'}, inplace=True)
            df['file_name_id'] = df['filename'].apply(lambda x: x.split('_')[2])
            df['Entity'] = df['filename'].apply(lambda x: x.split('_')[0])
            #extract date of article
            df['Article_Date'] = df['Article Text'].apply(lambda x: self.get_date(x))
            #clean text
            df['clean_text_for_coref'] = df['Article Text'].apply(lambda x: self.clean_for_coref(x, materialWord_list))                
        return df


#if '__name__==__main__':
#    cor_eng = CorefEngine()    
#    df = cor_eng.coref_orchestrator()
#    print(df)
#    text_data_path =  r'../data_new/text/sev/entity'
#    m_data = cor_eng.get_data(text_data_path)   
#    df = cor_eng.get_df_from_dict(m_data)
#    #rename cols
#    df.rename(columns={'article':'Article Text'}, inplace=True)
#    #clean text
#    df['clean_text_for_coref'] = df['Article Text'].apply(lambda x: CorefEngine().clean_for_coref(x))
#    
#    df['coref'] = df['clean_text_for_coref'].apply(lambda x: CorefEngine().get_coref(x))
#    print(df.shape)