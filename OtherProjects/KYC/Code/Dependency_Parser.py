# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 20:47:24 2019

@author: aarora33
"""

import spacy
from nltk.stem.snowball import SnowballStemmer
from Identity_Association import IdentityAssociation
import itertools

class DependencyParser(object):
    
    def __init__(self):
        self.stemmer = SnowballStemmer("english")
        self.nlp = spacy.load('en_coref_sm')
    
    def get_word_entity_relations(self, sentence, match_word):
        try:
            en_doc = self.nlp(sentence)
            left_list = []; dobj_list = []; pobj_list = [] 
            for token in en_doc:                           
                if token.text == match_word:                          
                    ancestors = token.ancestors
                    #check subject, Object up the tree from Word of Interest
                    for ancestor in itertools.chain([token], ancestors):      
                        for left in ancestor.lefts:                    
                            if(left.dep_ == 'nsubj' or left.dep_ == 'nsubjpass') and (left.pos_ == 'NOUN' or left.pos_ == 'PROPN'):
                                left_subject = ' '.join(list(map(str, left.lefts)))                                            
                                #merging compounds- Create func later
                                all_left_compounds = [' '.join(list(map(str, span.lefts))) for span in (list(left.lefts)) if ' '.join(list(map(str, span.lefts)))!='']
                                all_left_compounds = ' '.join(all_left_compounds)                        
                                merge_left_compounds = (all_left_compounds + ' '+ str(str(left_subject) +' ' + str(left.text)).strip()).strip()
                                left_list.append(merge_left_compounds)                
                        #check Object down the tree from Word of Interest
                    for right_token in token.rights:                
                        for right in right_token.subtree:                    
                            if(right.dep_ == 'dobj') and (right.pos_ == 'NOUN' or right.pos_ == 'PROPN'):                                         
                                right_dobj = ' '.join(list(map(str, right.lefts)))
                                #merging compounds
                                all_dobj_compounds = [' '.join(list(map(str, span.lefts))) for span in (list(right.lefts)) if ' '.join(list(map(str, span.lefts)))!='']
                                all_dobj_compounds = ' '.join(all_dobj_compounds)                        
                                merge_dobj_compounds = (all_dobj_compounds + ' '+ str(right_dobj + ' ' + right.text).strip()).strip()
                                dobj_list.append(merge_dobj_compounds)                                                    
                            elif(right.dep_ == 'agent' or right.dep_ == 'prep'):                                    
                                right_pobj = right.rights                    
                                for pobj in right_pobj:                            
                                    if(pobj.dep_ == 'pobj') and (pobj.pos_ == 'NOUN' or pobj.pos_ == 'PROPN'):                                                                                                             
                                        pobj_left_compound = ' '.join(list(map(str, pobj.lefts)))                                                                                                   
                                        #merging compounds
                                        all_pobj_compounds = [' '.join(list(map(str, span.lefts))) for span in (list(pobj.lefts)) if ' '.join(list(map(str, span.lefts)))!='']
                                        all_pobj_compounds = ' '.join(all_pobj_compounds)                                                        
                                        merge_pobj_compounds = (all_pobj_compounds + ' '+ str(pobj_left_compound + ' ' + str(pobj)).strip()).strip()
                                        if right.dep_ == 'prep' and right.text == 'by':
                                            pobj_list.append((merge_pobj_compounds, 'agent'))
                                        else:
                                            pobj_list.append((merge_pobj_compounds, right.dep_))                                                                    
            return left_list, dobj_list, pobj_list
        except:
            return [], [], []
        
    def find_dependency(self, subj, dobj, pobj, entity):  
        try:
            entity_dependency = False
            ia = IdentityAssociation()
            matched_entity, subj_flag = ia.match_entity(' '.join(subj), entity, {})
            matched_entity, dobj_flag = ia.match_entity(' '.join(dobj), entity, {})
            pobj_temp = [obj[0] for obj in pobj]
            matched_entity, pobj_flag = ia.match_entity(' '.join(pobj_temp), entity, {})
            pobj_prep_temp = [obj[0] for obj in pobj if obj[1] != 'agent']                        
            matched_entity, pobj_prep_flag = ia.match_entity(' '.join(pobj_prep_temp), entity, {})
            
            if (len(subj) == 0 and len(pobj) == 0):
                entity_dependency = None
            elif (subj_flag == False and dobj_flag == False and pobj_flag == False):        
                entity_dependency = None
                
            elif (len(subj) > 0 and len(dobj) > 0 and len(pobj)==0):
                if dobj_flag:
                    entity_dependency = True            
                #check if our entity is in obj: culprit
            elif (len(subj) > 0 and len(dobj) > 0 and len(pobj) > 0):                  
                if dobj_flag:
                    entity_dependency = True        
                elif pobj_prep_flag:
                    entity_dependency = True                   
                else:
                    entity_dependency = None
            #     #check if our entity is in obj or pobj: culprit
            elif (len(subj) > 0 and len(dobj) == 0 and len(pobj) > 0):        
                for obj in pobj:
                    matched_entity, is_entity = ia.match_entity(obj[0], entity, {})            
                    if obj[1] == 'prep' and is_entity: #add and condition for entity match
                        entity_dependency = True            
                        # if it is prep:culprit
                    elif obj[1] == 'agent':
                        matched_entity, is_entity = ia.match_entity(' '.join(subj), entity, {})
                        if(is_entity):                
                            entity_dependency = True
                    else:
                        matched_entity, is_entity = ia.match_entity(' '.join(subj), entity, {})
                        if(is_entity):
                            entity_dependency = True                    
            elif (len(subj) > 0 and len(dobj) == 0 and len(pobj) == 0):                  
                if subj_flag:
                    entity_dependency = True            
            #     #check if our entity is in subj: culprit
            elif (len(subj) == 0 and (len(dobj) >= 0 or len(pobj) >= 0)):    
                if dobj_flag:
                    entity_dependency = True            
                else:                
                    if(pobj_prep_flag):
                        entity_dependency = True                                                       
            return entity_dependency
        except:
            return None
#if '__name__==__main':
#    dp = DependencyParser()
#    sentence = "HDFC is fined by UBS bank for illegal transactions for $2 million."    
#    subj, dobj, pobj = dp.get_word_entity_relations(sentence, 'fined')
#    print(subj, dobj, pobj)
#    dep_flag = dp.find_dependency(subj, dobj, pobj, 'HDFC')
#    print('dep_flag is: ', dep_flag)