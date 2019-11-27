# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 16:13:56 2019

@author: aarora33
"""


import re
import pandas as pd
from datetime import date, datetime
now = datetime.now()

class Match_DOB(object):

    def __init__(self):
        pass
    def calculateAge_fromDate(self, inputDate) :
      today = date.today()
      return today.year - inputDate.year - ((today.month, today.day) < (inputDate.month, inputDate.day))
    
    
    def calculateAge_fromYear(self, inputYear):      
      inputYear = inputYear.strip()
      if inputYear.isdigit():
          if len(inputYear) == 2:
            inputYear_temp = '19' + inputYear
            age = int(now.year) - int(inputYear_temp)
            return age
          elif len(inputYear) == 4:
            age = int(now.year) - int(inputYear)
            return age
          else:
            return 0
      else:
        return 0
    
    def dateValidator(self, str1):
      date = datetime(1970,1,1)
      str1 = str1.strip()
      if re.search('\d{4}\.\d{1,2}\.\d{1,2}', str1):
        date = datetime.strptime(str1, '%Y.%m.%d')
        #print(date)
      elif re.search('\d{4}\-\d{1,2}\-\d{1,2}', str1):
        date = datetime.strptime(str1, '%Y-%m-%d')
        #print(date)
      elif re.search('\d{1,2}\.\d{1,2}\.\d{4}', str1):
        date = datetime.strptime(str1, '%d.%m.%Y')
        #print(date)
      elif re.search('\d{1,2}\-\d{1,2}\-\d{4}', str1):
        date = datetime.strptime(str1, '%d-%m-%Y')
      return datetime.strptime(date.strftime('%d.%m.%Y'), '%d.%m.%Y').date()
    
    
    def calculateAge(self, bdate):
      split_dob = re.compile(r'[\.|\-]')      
      matches = re.findall(split_dob, bdate)      
      if len(matches) >= 1:          
          dob = self.dateValidator(bdate)          
          age = self.calculateAge_fromDate(dob)          
          return age         
      else:          
          age = self.calculateAge_fromYear(bdate)          
          return age          
        
    def compareAge(self, row):            
        if pd.isnull(row[0]):
            return (False, True)
        else:
            input_DOB = str(row[0])
        article_DOB = row[1]
        split_dobpob = re.compile(r'\/')
        #split_dob = re.compile(r'[\.|\-]')
        input_age_list = []
        article_age_list = []      
      
        if re.search('\d+', article_DOB):
            input_age_list.append(self.calculateAge(input_DOB))            
          
        if article_DOB.strip() == '':
            return(False, True)
        if re.search('\d+', article_DOB):
            if re.search(split_dobpob, article_DOB):
                #print('/ Found')
                dob = re.split(r'\/', article_DOB)
              
                if dob[0] == '-':
                    return (False, True)          
                for value in dob[0].split(','):
                    article_age_list.append(self.calculateAge(value))
              
            else:
                for value in article_DOB.split(','):
                    article_age_list.append(self.calculateAge(value))
        else:
            return (False, True)
        print('article_age_list: ',article_age_list, 'input age list', input_age_list)
        
        if len(set(input_age_list).intersection(set(article_age_list))) > 0:
            return (True, True)
        else:
            flag = False
        for i in article_age_list:
          if i != 0:
            flag = True
            break
        if flag:
          return (False, False)
        else:
          return (False, True)


#if '__name__==__main':
#    mdob = Match_DOB()
#    match_flag, pass_flag = mdob.compareAge('1980.2.1', '1856')    
#    print(match_flag, pass_flag)