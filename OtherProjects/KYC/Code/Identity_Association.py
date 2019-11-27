# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 17:03:00 2018

@author: aarora33
"""
import spacy
import time
start_time = time.time()


import itertools
import re

class IdentityAssociation(object):
    
    def __init__(self):
        self.nlp = spacy.load('en_coref_sm')
        
    def getCombinations (self, lst):
        for i, j in itertools.combinations(range(len(lst) + 1), 2):
            yield lst[i:j]
            
    def check_nearabouts(self, sent, ent):
        flag = False
        sent = sent.lower()
        ent = ent.lower()
        if ent in sent:
            F = sent.find(ent)
            beforeStr=sent[(F-1):F]
            afterStr=sent[(F+len(ent)):(F+len(ent)+1)]
            beforeStr=re.sub('[^A-Za-z0-9]+', '', beforeStr)                              
            afterStr=re.sub('[^A-Za-z0-9]+', '', afterStr)                          
            if(beforeStr=="" and afterStr==""):
                flag = True
        return flag
        
    def exact_match(self, sentence, entity):
        matched_entity = None
        flag = False
        index = -1
        nlp_doc = self.nlp(sentence)
        lower_sentence = [word.lemma_ for word in nlp_doc]
        if len(entity.split()) > 1:        
            if entity.lower() in sentence.lower() and self.check_nearabouts(sentence, entity):     #exact match
                flag = True
                matched_entity = entity       
                index = sentence.lower().index(entity.lower())            
        else:
            if entity.lower() in lower_sentence:     #exact match
                flag = True
                matched_entity = entity      
                list_index = lower_sentence.index(entity.lower())
                l=0
                for i in lower_sentence[:list_index]:
                    l = l+len(i)
                index = l+list_index
        return index, matched_entity, flag        
    
    def partial_match(self, sentence, entity):
#        nlp_doc = self.nlp(sentence)    
        entity_list = entity.split()         
        flag = False
        index = -1
        for x in sorted(self.getCombinations(entity_list), key=len, reverse=True):
            flag = False
            if entity_list[0] in x:
                entity = ' '.join(x)            
#                lower_sentence = [word.lemma_ for word in nlp_doc]            
                if entity.lower() in sentence.lower() and self.check_nearabouts(sentence, entity):                
    #                 if is_entity(sentence):
                    flag = True               
                    index = sentence.lower().index(entity.lower())
                    return index, entity, flag
        return index, None, flag
        
    def initials_match(self, sentence, entity):
        initials = str()    
        flag = False
        for i in entity.split():
            initials = initials + i[0].upper()        
        sentence = list(filter(None, [re.sub(r'[^A-Za-z0-9]+', '', x) for x in sentence.split()]))    
        if initials in sentence:
            flag = True
            return initials, flag
        return None, flag
        
    def match_entity(self, sentence, entity, alias_dict):        
        alias_flag = False; flag = False 
        partial_alias_flag = False
        matched_entity = None
#        nlp_doc = self.nlp(sentence)
        doc_entity = self.nlp(str(entity).lower())
        entity = " ".join([token.orth_ for token in doc_entity if not(token.i==0 and token.is_stop) ])        
#        lower_sentence = [word.lemma_ for word in nlp_doc]            
        #alias match    
        aliases = alias_dict.items()
        for key, alias in aliases:                    
            index, matched_alias, alias_flag = self.exact_match(sentence, alias)
            if(alias_flag):                
                return matched_alias, alias_flag
            elif alias_flag == False:
                index, matched_entity, partial_alias_flag = self.partial_match(sentence, alias)        #partial match    
                if (partial_alias_flag):                    
                    return matched_alias, partial_alias_flag
        if(alias_flag == False and partial_alias_flag == False):
            #Exact Match
            index, matched_entity, flag = self.exact_match(sentence, entity)    
            if(flag):
                return matched_entity, flag
            elif flag==False and len(entity.split()) > 1:        
                index, matched_entity, flag = self.partial_match(sentence, entity)        #partial match    
                if (flag):
                    return matched_entity, flag
                elif flag == False:
                    matched_entity, flag = self.initials_match(sentence, entity)               #Initials Match
                    if(flag):
                        return matched_entity, flag            
                    elif flag==False:
                        #alternate entity reference check- Manually identified (loop if list size increases from 1)
                        entity = ['the bank']                        
                        if entity[0] in sentence.lower():
                            flag = True      
#                            matched_entity = entity[0]
            return matched_entity, flag
        
    def entity_related_text(self, row):
        text = row[0].replace('ltd.', 'ltd').replace('Ltd.','Ltd').replace('LTD.','LTD').replace(':', '-')
        entity = row[1].strip() #'KBC BANK'        
        raw_text = row[2]
        alias_dict = row[3]
        doc = self.nlp(str(text))
        raw_doc = self.nlp(str(raw_text))
        sentences = list(doc.sents)        
        raw_sentences = list(raw_doc.sents)        
        sentences_list = []
        raw_sentences_list = []
        matched_entity_set = set()
        if (len(sentences) == len(raw_sentences)):
            for i in range(0, len(sentences)):                
                matched_entity, flag = self.match_entity(str(sentences[i]), entity, alias_dict)
                if (flag):
                    raw_sentences_list.append(str(raw_sentences[i]))
                    sentences_list.append(str(sentences[i]))
                    if matched_entity != None:
                        matched_entity_set.add(matched_entity)
        else:
            for i in range(0, len(sentences)):            
                matched_entity, flag = self.match_entity(str(sentences[i]), entity, alias_dict)
                if (flag):
                    raw_sentences_list.append(str(sentences[i]))
                    sentences_list.append(str(sentences[i]))
                    if matched_entity != None:
                        matched_entity_set.add(matched_entity)                    
        entity_rel_score = round(len(raw_sentences_list)/len(raw_sentences),2)        
        return entity_rel_score, ' '.join(raw_sentences_list), ' '.join(sentences_list), list(matched_entity_set)
    
#if '__name__==__main__':
#    x = IdentityAssociation().match_entity(' HSBC and UB group of the group, is planning a USD150-million ' , 'UBS Group AG', alias_1='UB', alias_2='BU')
#    cor_eng = CorefEngine()    
#    df = cor_eng.coref_orchestrator()
#    df['coref'] = df['clean_text_for_coref'].apply(lambda x: cor_eng.get_coref(x))
#    ia = IdentityAssociation()    
#    df['entity_relevance_score'], df['entity_raw_text'], df['entity_text'], df['entity_found'] = zip(*df[['coref', 'entity', 'raw_text']].apply(ia.entity_related_text, axis=1))
#    print(df.shape)
#    print(df['entity_raw_text'])