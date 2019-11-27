# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 18:48:09 2019

@author: Manidipto
"""
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

import re    
import pandas as pd
import ast
import spacy

class CurrencyConverter(object):
    
    def __init__(self):
        self.nlp = spacy.load('en_coref_sm')
        pass
    
    def currency_excel_dataextraction(self, df):
        """
        defination: makes a dictonary of currencycode and all version of the currency.
        input: dataframe (of currency code stored in the system)
        Output: dictonary of currencycode and all version of the currency.
        """
        key=[]
        val=[]
        for ind,row in df.iterrows():
            key.append(row['Currency code'])
            val0=row['unique']
            val0 = ast.literal_eval(val0)
            
            val1=row['Units per USD']
            val.append((val0,val1))
        return(dict(zip(key,val)))
    
    def hasnumbers(self, inputString):
        """
        defination: checks whether a string has number in it
        input: string
        Output: True or False
        """
        return bool(re.search(r'\d+\.?\d*', inputString))
        
    def pre_processing(self, currencysym,inputstring):
        """
        defination:does preprocessing on the sentence and currency
        input: sentence and currencysymbol
        output: sentence and currencysymbol
        """
        try:
            s=inputstring.lower()
        except:
            s=inputstring
        s='dummy '+'dummy '+s+' dummy '+' dummy'+' dummy'
        try:
            code=currencysym.lower()
        except:
            code=currencysym
        stringg=s
        return code,stringg
    
    def combine_token(self, inputstring): ###'inidan rupee' to 'inidanrupee'
        """
        defination: combines all word of a sentence
        input: a sentence
        output: a singleword eg: 'inidian rupee: indianrupee'
        """
        outputword=''
        for m_token in inputstring.split():
            outputword+=m_token
        return outputword

    def amount_conv_todollar(self, all_currency_data,curr_code,unconvertedamount):
        """
        defination:convert amount(s) to dollar
        input:tupple constisting of different version of the cuurency code and amount,  currency code, dictonary of currencies
        output: list of all amounts converted to dollar
        """    
        allamount=[]
        rate=all_currency_data[curr_code][1]
        g=0
        for eachtup in unconvertedamount:
            if len(eachtup[1])==0:
                g+=1
                continue
            else:            
                for eachamount in eachtup[1]:                
                    allamount.append(( eachtup[0]+' ' +str(eachamount), round((eachamount/rate), 2)))
        return allamount  
    
    def find_multiple_word_currency(self, currency_code,inputstring):
        """
        defination:find presence of a currency (for two word currencies like: US dollar) in a string
        input: the currency(in str) and the string
        output: two lists, one of all words having the currency and other having the index of all those words
        """
        currencycode=currency_code.lower()
        inputstring=inputstring.lower()
        bills = ['mill','million','mll', 'mn', 'm', 'mln', 'M', 'bill','billion','bil', 'bn', 'b', 'bln', 'B', 'trill','trillion','tll', 'tn', 'thousand', 'lac', 'lacs', 'lakh', 'lakhs', 'crore', 'crores', 'cr']
        matches_words=[]
        matches_indesx=[]
        currency_tok=currencycode
        l_cur=len(currency_tok)
        input_tok=inputstring.split()
        temptoks=[]
        for i,inp_tok in enumerate(input_tok[2:-2]):
            temptok= input_tok[i]+' '+input_tok[i+1]
            temptoks.append(temptok)
            if currencycode in temptok:
                if self.hasnumbers(str(temptok)):
                    matches_words.append(temptok)
                    matches_indesx.append(i)
                else:
                    t= input_tok[i]+' '+input_tok[i+1]+' '+input_tok[i+2]+' '+input_tok[i-1]+' '+input_tok[i-2]
                    for bill in bills:
                        if bill in temptok:
                            if self.hasnumbers(str(input_tok[i-1])):
                                matches_words.append(t)
                                matches_indesx.append(i)
                    if not self.hasnumbers(str(input_tok[i-1])):
                        if self.hasnumbers(t):
                            matches_words.append(t)
                            matches_indesx.append(i)
        return matches_words,matches_indesx
        
    def mul_curr_find_mill_bill_trill(self, currencycode,inputstring,matches_words,matches_indesx):
        """
        defination:find presence of a million,billion,trillion etc beside the ouputs of find_multiple_word_currencies.
                   the list of million,billion,trillion used here should be separately provided by the user
        input: the currency(in str), the string and the outputs of find_multiple_word_currencies
        output:a list of output of find_multiple_word_currencies append with billion,million etc.
        """
        mill_bill_list_val= ['million','billion','trillion', 'thousand', 'lac', 'crore']
        mill_bill_list= [['mill','million','mll', 'mn', 'm', 'mln', 'M'],
                            ['bill','billion','bil', 'bn', 'b', 'bln', 'B'],
                            ['trill','trillion','tll', 'tn'],
                            ['thousand'],
                            ['lac', 'lacs', 'lakh', 'lakhs'],
                            ['crore', 'crores', 'cr']]
        mill_bill_dict=dict(zip(mill_bill_list_val,mill_bill_list))
        tokens=inputstring.split()
        for ind_match,token_no in enumerate(matches_indesx):
                brk=0
                for key,value in mill_bill_dict.items():
                    initial_token = []
                    for eachval in value:                                        
                        temp_tok=[tokens[token_no], tokens[token_no+1], tokens[token_no+2], tokens[token_no+3], tokens[token_no-1], tokens[token_no-2], tokens[token_no-3]]
                        temp_tok = [x.lower() for x in temp_tok]
                        for tok in temp_tok:                        
                            if re.search('\d+\.?\d*', tok):
                                initial_token = tok
                                break
                        if eachval in initial_token:
                            matches_words[ind_match]+=key                        
                            brk=1             
                            break
                        elif eachval in temp_tok:
                            if re.search('\d+\.?\d*',temp_tok[temp_tok.index(eachval)-1]):
                                matches_words[ind_match]+=key
                                brk=1               
                                break
                        else:
                            continue
                if brk==1:
                    break
        return matches_words 


    def find_currency(self, currencycode,inputstring):
        """
        defination:find presence of a currency (for one word currencies like: USdollar or usd) in a string
        input: the currency(in str) and the string
        output: two lists, one of all words having the currency and other having the index of all those words
        """
        x1_sym = []; x_sym = []
        s=inputstring
        bills = ['mill','million','mll', 'mn', 'm', 'mln', 'M', 'bill','billion','bil', 'bn', 'b', 'bln', 'B', 'trill','trillion','tll', 'tn', 'thousand', 'lac', 'lacs', 'lakh', 'lakhs', 'crore', 'crores', 'cr']
        D1,s=self.pre_processing(currencycode,inputstring)
        #Check if the string starts with "The":
        command_curr_all=""+D1
        matches_words=[]
        matches_indesx=[]
        tokens=s.split()
        if len (command_curr_all.split())==1:
            if len(command_curr_all)>1:##multiple word currency version='USD'
                for ind,token in enumerate(tokens):
                    if command_curr_all == token:        
                        if self.hasnumbers(token):            
                            try:
                                matches_words.append(token)                          
                                matches_indesx.append(ind)
                            except:
                                continue
                        else:
                            temp_token=tokens[ind]+tokens[ind-1]+tokens[ind-2]+tokens[ind+1]+tokens[ind+2]
                            temp_token1=[tokens[ind-2],tokens[ind-1],tokens[ind],tokens[ind+1],tokens[ind+2]]
                            digits = 0
                            for x in temp_token1:
                                if x.isdigit():
                                    digits+=1
                            if digits > 1:
                                var1 = set(bills).intersection(set(temp_token1))
                                temp = ''
                                for x in var1:
                                    temp = ''+x
                                if temp != '':
                                    if not temp_token1.index(temp) == 0:
                                        if self.hasnumbers(temp_token1[temp_token1.index(temp)-1]):
                                            amount = re.search('\d+\.?\d*', temp_token1[temp_token1.index(temp)-1])
                                            try:
                                                matches_words.append(token + amount.group(0))                          
                                                matches_indesx.append(ind)
                                            except:
                                                continue
                                else:
                                    for num in temp_token1:
                                        if num.isdigit():
                                            matches_words.append(num)
                                    try:
                                        matches_words.append(token + amount.group(0))                          
                                        matches_indesx.append(ind)
                                    except:
                                        continue
                            else:        
                                amount = re.search('\d+\.?\d*', temp_token)##check whether there is a number inside text
                                try:
                                    matches_words.append(token + amount.group(0))                          
                                    matches_indesx.append(ind)
                                except:
                                    continue
                return matches_words,matches_indesx
            else: ##single word currency version=='S' or 'N',only left is considered,no right            
                c=command_curr_all
                for ind,token in enumerate(tokens):                    
                    x = re.findall(r'\b'+c+'\d+\.?\d*\s*[a-z]*', token)##check whether a symbol like a letter (N)is present                     
                    if not c.isalpha():
                        x_sym=re.findall(r'[' +c+ ']\s*\d+\.?\d*\s*[a-z]*', token)##check whether a symbol special char ($)is present 
                    if len(x)>0 or len(x_sym)>0:        
                        matches_words.append(token)
                        matches_indesx.append(ind)
                    elif token==command_curr_all:     ###only at left
                        temp_token=tokens[ind]+tokens[ind+1]
                        x = re.findall(r'\b'+c+'\d+\.?\d*\s*[a-z]*', temp_token)##check whether a symbol like a letter (N)is present                                             
                        if not c.isalpha():                    
                            x_sym=re.findall(r'[' +c+ ']\s*\d+\.?\d*\s*[a-z]*', temp_token)##check whether a symbol special char ($)is present 
                        temp_token1=tokens[ind-1]+tokens[ind]
                        x1= re.findall(r'\b'+c+'\d+\.?\d*\s*[a-z]*', temp_token1)##check whether a symbol like a letter (N)is present                         
                        if not c.isalpha():
                            x1_sym=re.findall(r'[' +c+ ']\s*\d+\.?\d*\s*[a-z]*', temp_token1)##check whether a symbol special char ($)is present 
                        if len(x)>0 or len(x_sym)>0:
                            matches_words.append(temp_token)
                            matches_indesx.append(ind)
                        elif len(x1)>0 or len(x1_sym):
                            matches_words.append(temp_token1)
                            matches_indesx.append(ind)
                    else:
                        continue
                return matches_words,matches_indesx
        else:
            return([],[])
                     
    def find_mill_bill_trill(self, currencycode,inputstring,matches_words,matches_indesx):
        """
        defination:find presence of a million,billion,trillion etc beside the ouputs of find_multiple_word_currencies.
                   the list of million,billion,trillion used here should be separately provided by the user
        input: the currency(in str), the string and the outputs of find_multiple_word_currencies
        output:a list of output of find_currency appended with billion,million etc.(if they are present)
        """
        if len(currencycode.split())==1:
            D1,s=self.pre_processing(currencycode,inputstring)        
            matches_words=matches_words
            matches_indesx=matches_indesx
            tokens=s.split()
            mill_bill_list_val= ['million','billion','trillion', 'thousand', 'lac', 'crore']
            mill_bill_list=[['mill','million','mll', 'mn', 'm', 'mln', 'M'],
                            ['bill','billion','bil', 'bn', 'b', 'bln', 'B'],
                            ['trill','trillion','tll', 'tn'],
                            ['thousand'],
                            ['lac', 'lacs', 'lakh', 'lakhs'],
                            ['crore', 'crores', 'cr']]
            mill_bill_dict=dict(zip(mill_bill_list_val,mill_bill_list))
            for ind_match,token_no in enumerate(matches_indesx):
                brk=0
                for key,value in mill_bill_dict.items():
                    initial_token = []
                    for eachval in value:
                        temp_tok=[tokens[token_no], tokens[token_no+1], tokens[token_no+2], tokens[token_no-1], tokens[token_no-2]]                                        
                        temp_tok = [x.lower() for x in temp_tok]
                        for tok in temp_tok:                        
                            if re.search('\d+\.?\d*', tok):
                                initial_token = tok
                                break
                        if eachval in initial_token:
                            matches_words[ind_match]+=key                        
                            brk=1             
                            break
                        elif eachval in temp_tok:
                            if re.search('\d+\.?\d*',temp_tok[temp_tok.index(eachval)-1]):
                                matches_words[ind_match]+=key
                                brk=1               
                                break
                        else:
                            continue
                    if brk==1:
                        break
        else:
            pass
        return matches_words  
    
    def mull_full_func_currencyconv(self, currencysym,inputstring,conversionrate=1.0):
        """
        defination:gives the currency amount in the sentence (for two words currency)
        input: currency,sentence(s)
        output:a tupple of currency and the amount obtained from the sentence.
        """
        matches_words,matches_indesx=self.find_multiple_word_currency(currencysym,inputstring)
        matches_words1 =  self.mul_curr_find_mill_bill_trill(currencysym,inputstring, matches_words,matches_indesx)
        convereted_num=[float(re.findall('\d+\.?\d*', str1 )[0])*(self.conv_to_num(str1)*conversionrate) for str1 in matches_words1 ]
        return(currencysym,convereted_num)

    def  conv_to_num(self, curr):
        """
        defination:converts million,billion, trillion, thousand, lac, crore to 10^6,10^9 and 10^12
        input: alphanumberic string
        output:10^6 or 10^9 or 10^12 or 1
        """
        mill_bill_list=['million','billion','trillion', 'thousand', 'lac', 'crore']
        mill_bill_list_val=[10**6, 10**9, 10**12, 10**3, 10**5, 10**7]
        for i in range(6):
            if mill_bill_list[i] in curr:
                return mill_bill_list_val[i]
        return 1
    
    def full_func_currencyconv(self, currencysym,inputstring,conversionrate=1.0):
        """
        defination:gives the currency amount in the sentence (for 1 word currency)
        input: currency,sentence(s)
        output:a tupple of currency and the amount obtained from the sentence.
        """
        matches_words,matches_indesx=self.find_currency(currencysym,inputstring)
        matches_words1=  self.find_mill_bill_trill(currencysym,inputstring, matches_words,matches_indesx)
        convereted_num=[float(re.findall('\d+\.?\d*', str1 )[0])*(self.conv_to_num(str1)*conversionrate) for str1 in matches_words1 ]
        return(currencysym,convereted_num)
    
    def all_currency_conversion (self, all_currency_dict,unique_codeofcurrency,sentence): ##convert amount of mill_billion to numbers
        """
        defination:gives the currency amount in the sentence (for 1 word currency)
        input: currency dictonary obtained from currency_excel_dataextraction function ,currency code,sentence(s)
        output:a tupple of lists of difference versions of a currency and the amount obtained from the sentence.
        """
        all_curr=all_currency_dict[str(unique_codeofcurrency)]
        currencies_list=all_curr[0]
        all_finds=[]
        for each_symbols in currencies_list:
            if len(each_symbols.split())==1:
                sym = self.full_func_currencyconv(each_symbols,sentence)
                if len(sym[1]) != 0 : 
                    all_finds.append(sym)
            else:
                combinedword=self.combine_token(each_symbols)
                sym = self.full_func_currencyconv(combinedword,sentence)
                if len(sym[1]) != 0 : 
                    all_finds.append(sym)
                sym1 = self.mull_full_func_currencyconv(each_symbols,sentence)
                if len(sym1[1]) != 0 : 
                    all_finds.append(sym1)
                ##version 2 for inidan rupee
        return all_finds
    
    def extract_amount(self, sentence, currency_db):
        doc = self.nlp(sentence)
        sentence = [word.text for word in doc if not word.is_punct]
        sentence = " ".join(sentence)
        ###important
        sentence= ' dummy dummy dummy dummy ' + sentence + ' dummy dummy dummy dummy ' 
        amount_dict = {}
        unconverted_amount_list = []
        converted_amount_list = []
        for cur in currency_db:
            ####user input(the code of currency i.e. INR for Indian Rupee)
            country_code=cur
            unconverted_amount=self.all_currency_conversion (currency_db,country_code,sentence)    
            amount = self.amount_conv_todollar(currency_db,country_code,unconverted_amount)
            if len(amount) > 0:
                for i in unconverted_amount:
                    if len(i[1]) > 0:
                        unconverted_amount_list.append(i)                
                converted_amount_list.extend(amount)
        amount_dict['actual_amount'] = unconverted_amount_list        
        amount_dict['dollar_amount'] = converted_amount_list    
        return amount_dict

if __name__=='__main__':
    cc = CurrencyConverter()
    cureency_df=pd.read_excel('../corpus/curency_data_unique.xlsx') ##data extraction from excel
    currency_db = cc.currency_excel_dataextraction(cureency_df)###the dictonary of all currency codes
    sentence='CFTC Orders Citibank  Japanese EUR2m Affiliates to Pay  $175 million Penalty 87 Dow Jones & Company Inc.'
    amount_dict = cc.extract_amount(sentence, currency_db)
    print(amount_dict)