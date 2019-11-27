import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import pandas as pd
from itertools import permutations
from fuzzywuzzy import fuzz
import os
import re
from bs4 import BeautifulSoup
import statistics 
import datetime    
import json
import copy
import config_file as cf
import shutil
import numpy as np
import ast
import nltk
from nltk.util import ngrams

shutil.rmtree(cf.cl_txt_files_path)
os.mkdir(cf.cl_txt_files_path)     

input_list = ['Name', 'Query', 'Data Pool(s)', 'Min Relevance', 'Nationality', 'Domicile', 'Birthdate or Birthyear', 'Max Results', 'Synonym', 'Consider Initials']
input_match_list = ['Name', 'First Name', 'Aliases', 'Alt. spelling', 'Risk', 'Category', 'Subcategory', 'Data pool', 'Title', 'Position', 'Age',
                    'Birthdate / Place of birth', 'Deceased', 'Passports / SSN', 'Locations', 'Country', 'Related companies', 'Related individuals',
                    'Further Information', 'Keywords', 'History url', 'External Sources', 'Other systems links', 'First Entered in source', 'Last Updated in source']

def convert_pdf(path, format='html', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()    
    return text

## cl extraction

# write decorator for taking list as input and run below function and get the output if name macthed-Flag

#def check_name_combinations(name_1,name_2,type_flag):
#    print("checking" ,name_1,'----',name_2)
#    ratios = []
#    if(type_flag == "alias"):
#        if  ',' in name_1:
#            names = name_1.split(',')            
#            for name in names:                                
#                x = name.split()
#                if len(x) <= len(name_2.split()) + 2:
#                    print('x is:', x)                
#    #                if len(x) 
#                    comb = []
#                    perm = permutations(x)
#                    print('\n---------------perm is:', len(list(perm)))
#                    print(list(perm)[0])
#                    for num in perm :
#                        comb.append(" ".join(num))
#                    for c in comb:
#        #                print("alias matching-----",name_2,"----",c)
#                        ratios.append(fuzz.ratio(name_2,c))
#        else:
#            #change this logic later
#             ratios.append(fuzz.ratio(name_2,name_1))
##        print('alias ratios: ', ratios)
#    else:
#        x = name_1.split()
#        comb = []
#        perm = permutations(x)
#        for num in perm :
#            comb.append(" ".join(num))
#        for c in comb:
##            print("name matching-----",name_2,"----",c)
#            ratios.append(fuzz.ratio(name_2,c))
##        print('name ratios: ', ratios)
#    return max(ratios) 

def word_grams(words, min_len, max_len):
    s = []
    for n in range(min_len, max_len):
        for ngram in ngrams(words, n):
            s.append(' '.join(str(i) for i in ngram))
    return s

def check_name_combinations(name_1,name_2,type_flag):    
    ratios = []
    if(type_flag == "alias"):                        
        alias_list = name_1.split('\n')        
        names = []
        for i in alias_list:
            names.extend(i.split(','))        
        for name in names:              
            x = name.split()                        
            if len(x) <= 7 :
                comb = []
                perm = permutations(x)                
                for num in perm :
                    comb.append(" ".join(num))                
                for c in comb:                    
                    ratios.append(fuzz.ratio(name_2,c))
            else:
                first_half = x[: (int(len(x) / 2))]
                other_half = x[(int(len(x) / 2)): ]
                if len(other_half) <= 7:
                    comb = []
                    comb.extend(first_half)
                    perm = permutations(other_half)                
                    for num in perm :
                        comb.append(" ".join(num))                    
                    for c in comb:                        
                        ratios.append(fuzz.ratio(name_2,c))
                    
                else:
                    ratios.append(0)
        if max(ratios) == 0:
            name_len = len(name_2.split())
            alias = " ".join(name_1.split('\n')).split()            
            n_grams = word_grams(alias, name_len-2, name_len+3)             
            for n in n_grams:
                ratios.append(fuzz.ratio(name_2,n.lower()))
            
    else:
        x = name_1.split()
        if len(x) <= 7 :
            comb = []
            perm = permutations(x)            
            for num in perm :
                comb.append(" ".join(num))            
            for c in comb:                
                ratios.append(fuzz.ratio(name_2,c))
        else:
            first_half = x[: (int(len(x) / 2))]
            other_half = x[(int(len(x) / 2)): ]
            if len(other_half) <= 7:
                comb = []
                comb.extend(first_half)
                perm = permutations(other_half)                
                for num in perm :
                    comb.append(" ".join(num))                
                for c in comb:                    
                    ratios.append(fuzz.ratio(name_2,c))
            else:
                ratios.append(0)
    return max(ratios)

def check_name_combinations_decorator(func):
    def inner(input_name, alias_list, type_):                       
        if not isinstance(alias_list, list):
            alias_list = ast.literal_eval(str(alias_list))
        match_list = []
        for alias in alias_list:                                    
            match = func(input_name, alias, type_)                   
            match_list.append(match)        
        return max(match_list)
    return inner
        
###### folder path of pdf files
################ Fetched Organisation name using the file name of pdf ####
direc = cf.cl_folder_path
text_folder_list = os.listdir(direc)
dir_flag = True
for item in text_folder_list:
    print('staring file: ', item)
    org_name = item.split('.')
    if(len(org_name) == 2):
        org_name = org_name[0]
    elif(len(org_name) > 2):
        org_name = ' '.join(org_name[:len(org_name)-1])

################ Extracted the content of pdf, convert_pdf is the function for the extraction ####
################ Input to convert_pdf is the file path, fname = folder_path(direc) + file_name(item) ####  
################ Extracted all the data which is present in the span tag and after removing the junk - ##
################ values, stored in a dataframe named data. ####
    filename = item                                                                       
    fname = os.path.join(direc, item)    
    x_html = convert_pdf(fname)
    soup = BeautifulSoup(x_html, "html.parser")
    span_data = soup.find_all('span')
    text_df = r'C:\Users\aarora33\News_Screening_KYC\data_new\intermediate_CL\text.txt'
    
    data =  []
    for item in span_data:
    # for item in div_data:
        temp = item.text
        data.append(temp)
    data = [item for item in data if item != '']
    data = [item for item in data if item != ' ']
    data = [re.sub(':', '', item) for item in data]
    data = [re.sub('\\n', '', item) for item in data]
    data = [re.sub('\\xa0', '', item) for item in data]
    data = [item for item in data if item != '']
    data = {'c1' : data}
    data = pd.DataFrame(data)  
    print('initial dataframe created')         
    
    #saving intermediate dataframe
    if dir_flag:
        shutil.rmtree(cf.cl_excel_files_path)    
        os.mkdir(cf.cl_excel_files_path)
        dir_flag = False
    excel_df = filename + '.csv'
    data.to_csv(os.path.join(cf.cl_excel_files_path, excel_df), sep='@')
#    with open(text_df, 'w') as f:
#        f.write(str(soup.encode("utf-8")))
######## data_path is folder path of excel file, if saved in any folder.
######## Run the code from here after uncommenting the below lines, if you have
######## converted excel files of pdfs.
##==============================================================================
##     
##    data_path = r'../data/pdf_data/cl/pdf_to_excel'
##    folder_list = os.listdir(data_path)
##    for item in folder_list:
##         org_name = item.split('.')
##         if(len(org_name) == 2):
##             org_name = org_name[0]
##         elif(len(org_name) > 2):
##             org_name = ' '.join(org_name[:len(org_name)-1])
##         try:
##             data = pd.read_csv(os.path.join(data_path, item))
##         except:
##             pass
##==============================================================================
#    
############# Sometimes duplicate data get fetched, so the below code remove all the duplicate data ##
#    data_duplicate = copy.deepcopy(data)        
    dup_data_inx = []
    for index, row in data.iterrows():
       temp = row['c1']
       if(temp == 'For Internal use only'):
           dup_data_inx.append(index)
           break
    
    
    if(len(dup_data_inx) > 1):       
        data = data[dup_data_inx[0]:]
    data = data.reset_index(drop=True) 
    def get_hits(text):
        temp_str = np.nan
        if(re.search('\d{1}Hit\d{1,3}\S*\s*', text)):                        
            temp_str = re.findall('\d{1}Hit\d{1,3}\S*\s*', text)[0]
            return text.strip().lower()
        return temp_str
    data['hits'] = data['c1'].apply(get_hits)    
    
    #get unique dataframse set
    
    flag = True
    unique_hits = set()    
    for i, v in data.iterrows():
        if i==0:
            data.loc[i,'hits'] = 'initial'
            continue        
        if pd.notnull(data['hits'].iloc[i-1]) : # and pd.isnull(data['hits'].iloc[i]):            
#                unique_hits[data['hits'].iloc[i-1]] = 1            
            if pd.isnull(data['hits'].iloc[i]):
                if data['hits'].iloc[i-1] not in unique_hits:                                    
                    data.loc[i,'hits'] = data['hits'].iloc[i-1]                                 
                    flag = False
                else:
                    data.loc[i-1,'hits'] = np.nan
            else:
                if data['hits'].iloc[i-1] != data['hits'].iloc[i]:
                    unique_hits.add(data['hits'].iloc[i-1])
                continue
        else:
            if flag:                                
                data.loc[i,'hits'] = 'initial'
    data = data[data['hits'].notnull()]
#    
#    
############## Finding the first and the last row indices from the entire dataframe that have entity informations, e.g Name, ##
############## Query, Data pools etc #####        
    flag = 0
    temp_inx1 = 6
    for index, row in data.iterrows():
        temp1 = row['c1']    
        if(temp1 == 'CS Global Check Engine'):
            temp_inx = index
            if(data['c1'].iloc[temp_inx + 3] == 'Search Criteria'):
                temp_inx1 = temp_inx + 4
                flag = 1
        elif(temp1 == 'Legal Notice'):
            temp_inx2 = index            
            break
#        
#
############# Input_dict is the dictionary that has values of 'Name', 'Query', 'Data Pool(s)', ########
############# 'Min Relevance', 'Nationality', 'Domicile', 'Birthdate or Birthyear', 'Max Results', #######
############# 'Synonym', 'Consider Initials' ######
############# Matched the element of input_list one by one after iterating over the dataframe in between ###
############# the indices find above, also matched the next elemnet of the current item of the input_list ##
############# and subset the rows in between the current item and the next item, assigned as the value ###
############# to the key of input_dict which is the current item of the input_list. ###        
    print('starting dataframe parsing for search query inputs')
    input_dict = {}          
    if(flag == 1):
        for i in range(len(input_list)-1):
            for j in range(temp_inx1, temp_inx2):
                if((input_list[i] == data['c1'].iloc[j]) and (input_list[i+1] == data['c1'].iloc[j+1])):
                    val = ''
                    temp_inx1 = j+1
                    # print('Hello1')
                    break
                elif((input_list[i] == data['c1'].iloc[j]) and (input_list[i+1] == data['c1'].iloc[j+2])):
                    val = data['c1'].iloc[j+1]
                    temp_inx1 = j+2
                    # print('Hello2')
                    break
                elif((input_list[i] == data['c1'].iloc[j]) and (input_list[i+1] == data['c1'].iloc[j+3])):
                    val = data['c1'].iloc[j+1] + ' ' + data['c1'].iloc[j+2]
                    temp_inx1 = j+3
                    # print('Hello3')
                    break
                elif((input_list[i] == data['c1'].iloc[j]) and (input_list[i+1] == data['c1'].iloc[j+4])):
                    val = data['c1'].iloc[j+1] + ' ' + data['c1'].iloc[j+2] + ' ' + data['c1'].iloc[j+3]
                    temp_inx1 = j+4
                    # print('Hello4')
                    break
                elif((input_list[i] == data['c1'].iloc[j]) and (input_list[i+1] == data['c1'].iloc[j+5])):
                    val = data['c1'].iloc[j+1] + ' ' + data['c1'].iloc[j+2] + ' ' + data['c1'].iloc[j+3] + ' ' + data['c1'].iloc[j+4]
                    temp_inx1 = j+5
                    # print('Hello5')
                    break
                elif((input_list[i] == data['c1'].iloc[j]) and (input_list[i+1] == data['c1'].iloc[j+6])):
                    val = data['c1'].iloc[j+1] + ' ' + data['c1'].iloc[j+2] + ' ' + data['c1'].iloc[j+3] + ' ' + data['c1'].iloc[j+4] + ' ' + data['c1'].iloc[j+5]
                    temp_inx1 = j+6
                    # print('Hello6')
                    break
                else:
                    val = ''
                    temp_inx1 = temp_inx1 + 1
                    # print(input_list[i], input_list)
                    # print('Hello7')
                    break
            input_dict[input_list[i]] = val
    
    if(temp_inx2 - temp_inx1 == 3):
        input_dict[input_list[len(input_list)-1]] = data['c1'].iloc[temp_inx1 + 1]
#        print('-----', input_dict)
######## Checked the Number of results, if more than zero then further code will run else no ###
        
    total_res = data['c1'].iloc[temp_inx2-1]
    total_res = re.findall('\d{1,3}\s*', total_res)
    
    if(total_res == []):
        continue   

######### Found indices of all the Hits ###
    
    total_res = total_res[0].strip()
    total_res = int(total_res)    
    input_match_inx = []
    data1 = data[temp_inx2:len(data.index)]
    data1 = data1.reset_index(drop=True) 
#    
    for index, row in data1.iterrows():
        temp_str = row['c1']    
        # if(re.search('\d{1}\.\d{1,2}\S*\s*', temp_str)):
        if(re.search('\d{1}Hit\d{1,3}\S*\s*', temp_str)):            
            # temp_str = re.findall('\d{1}\.\d{1,2}\S*\s*', temp_str)
            temp_str = re.findall('\d{1}Hit\d{1,3}\S*\s*', temp_str)
            print('temp_str-------------', temp_str)
            # print(temp_str[0])
            if(len(temp_str[0].strip()) < 9):
                input_match_inx.append(index)
                
    # diff_in_inx = [x - input_match_inx[i - 1] for i, x in enumerate(input_match_inx)][1:]
    # avg_diff_in_inx = sum(diff_in_inx)/len(diff_in_inx)
   
############# Master_input_dict is the dictionary of dictioanry that has relevant information of all the entities found ######
############# Hit1, Hit2, etc are the keys and the corresponding data are the values. ####
############# here also matched the each element of input_match_list, subset the rows between the current #####
############# and the next element, assigned those rows as a value to current element which is a key input_match_list_dict ##.
    print('starting dataframe parsing for hits')
    master_input_dict = {}
    master_key = []
    master_value = []
    for i in range(len(input_match_inx)):
        key = data1['c1'].iloc[input_match_inx[i]]
        key = key.split('Hit')[1]
        key = 'Hit' + key                     
        initial_name_index = 0
        master_key.append(key)
        if(i+1 < len(input_match_inx)):
            temp_data = data1[input_match_inx[i] : input_match_inx[i+1]]
            temp_data = temp_data.reset_index(drop=True)
#==============================================================================
#         elif(i+2 == len(input_match_inx)):
#             print('Hello2')
#             temp_data = data1[input_match_inx[i+1] : len(data1.index)]
#             temp_data = temp_data.reset_index(drop=True)
#             print(temp_data['c1'].iloc[0])
#             print(temp_data['c1'].iloc[len(temp_data)-1])
#==============================================================================
        elif(i+1 == len(input_match_inx)):
            temp_data = data1[input_match_inx[i] : len(data1.index)]
        input_match_list_dict = {}
        for j in range(len(input_match_list)-1):
            k_temp = 0
            flag1 = 0
            flag2 = 0
            flag3 = 0
            for k in range(k_temp, len(temp_data)):
                if((input_match_list[j] == temp_data['c1'].iloc[k]) and (flag1 == 0)):
#                    print('input names', input_match_list[j])
                    if initial_name_index == 0:
                        initial_name_index = k
                    inx1 = k
                    flag1 = 1
                    flag2 = 1
                if((input_match_list[j+1] == temp_data['c1'].iloc[k]) and (flag2 == 1)):    
                    inx2 = k
                    k_temp = k
                    flag3 = 1
                    break
            val = ''
            inx_diff = inx2 - inx1
            if((flag3 == 1) and (inx_diff > 1)):
                for l in range(inx1 + 1, inx2):
                    val = val + temp_data['c1'].iloc[l] + ' '            
            input_match_list_dict[input_match_list[j]] = val
            input_match_list_dict[temp_data['c1'].iloc[k_temp]] = temp_data['c1'].iloc[k_temp + 1]
        hit_name_df = pd.DataFrame(temp_data['c1'].iloc[:initial_name_index])
        hit_name = hit_name_df['c1'].iloc[2:3].values[0]    
        print('hitname', hit_name)
        input_match_list_dict['hit_name'] = hit_name        
        master_input_dict[key] = input_match_list_dict 

############## Once done with the extraction of relevant data, below checked if the Name or Alias is the
############## same as the Name or Alias of the original entity, if yes then fethched the Subcategory,
##############  Locations, Country and Further information, put it in a JSON and dumped it in the folder
############## location report path.     
    del data
    del data1    
    final_output = {}  
    final_output1 = {}
    report = {}
    sub_category = {}  
    text_temp = []   
    org_name1 = org_name          
    counter = 0     
    for key in master_input_dict:   
        print('hits--------', key)        
#        if counter == 10:
#            break
        counter += 1
        lst = []
        temp_output_dict = {}
        flag_name = 0
        flag_alias = 0
        flag_partial = 0
#        print('namesssssssssssssss', master_input_dict[key]['Name'], input_dict['Name'])
        if(master_input_dict[key]['hit_name'].strip().lower() == input_dict['Name'].strip().lower()):
            flag_name = 1
        elif(master_input_dict[key]['Name'].strip().lower() == input_dict['Name'].strip().lower()):
            flag_name = 1
        elif(len(master_input_dict[key]['Aliases'].strip().lower()) == len(input_dict['Name'].strip().lower())):
            if(master_input_dict[key]['Aliases'].strip().lower() == input_dict['Name'].strip().lower()):
                flag_alias = 1
        elif(len(master_input_dict[key]['Aliases'].strip().lower()) > 1.5 * len(input_dict['Name'].strip().lower())):
            input_name1 = input_dict['Name']
            input_name = input_dict['Name']
            input_name = input_name.split(' ')[0].strip()
            master_alias = master_input_dict[key]['Aliases']
            try:
                master_alias = master_alias.split(input_name)
            except:
                master_alias = ''
            master_alias_name = []
            if(len(master_alias) > 1):
                for item in master_alias:
                    temp = ''
                    temp = temp.strip() + input_name.strip() + ' ' + item.strip()
                    temp = temp.strip()
                    master_alias_name.append(temp)
            if(input_name1 in master_alias_name):
                flag_alias = 1
    #    print('aliases-------------------', master_input_dict[key]['Aliases'].strip().lower(),'----' ,input_dict['Name'].strip().lower())        
        partial_match_hit_name = check_name_combinations(master_input_dict[key]['hit_name'].strip().lower(), input_dict['Name'].strip().lower(), 'name')        
        print('checking hitname combination', partial_match_hit_name)
    #    print('hit ratio: ', partial_match_hit_name, master_input_dict[key]['hit_name'].strip().lower(), input_dict['Name'].strip().lower())        
        partial_match_name = check_name_combinations(master_input_dict[key]['Name'].strip().lower(), input_dict['Name'].strip().lower(), 'name')
        print('checking name combination', partial_match_name)        
        print('aliases.....................................',master_input_dict[key]['Aliases'].strip().lower())
        partial_match_alias = check_name_combinations(master_input_dict[key]['Aliases'].strip().lower(), input_dict['Name'].strip().lower(), 'alias')            
        print('checking aliases combination', partial_match_alias)
        match_ratio = 60
        if(partial_match_hit_name >= 80):
            flag_partial = 1
            match_ratio = partial_match_hit_name
        elif(partial_match_name >= 80):
            flag_partial = 1
            match_ratio = partial_match_name
        elif(partial_match_alias >= 80):
            flag_partial = 1
            match_ratio = partial_match_alias
        if(flag_name or flag_alias or flag_partial == 1):
            temp_output_dict['hit_status'] = 'true_hit'            
        else:
            temp_output_dict['hit_status'] = 'false_positive'
        # lst.append('Subcategory :')
        # lst.append(master_input_dict[key]['Subcategory']  + ' ,,,')
        temp_output_dict['hit_name'] = master_input_dict[key]['hit_name'].strip().lower()                  
        temp_output_dict['match_ratio'] = match_ratio                        
        temp_output_dict['Subcategory'] = master_input_dict[key]['Subcategory'].strip()
            # lst.append('Locations :')
            # lst.append(master_input_dict[key]['Locations'] + ' ,,,')
        temp_output_dict['Locations'] = master_input_dict[key]['Locations'].strip()
        # lst.append('Country :')
        # lst.append(master_input_dict[key]['Country'] + ' ,,,')
        temp_output_dict['Country'] = master_input_dict[key]['Country'].strip()
        # lst.append('Further information :')
        # lst.append(master_input_dict[key]['Further Information'] + ' ,,,')
        temp_output_dict['Category'] = master_input_dict[key]['Category'].strip()
        temp_output_dict['Risk'] = master_input_dict[key]['Risk'].strip().lower()
        temp_output_dict['Age'] = master_input_dict[key]['Age'].strip()
        temp_output_dict['DOB_POB'] = master_input_dict[key]['Birthdate / Place of birth'].strip()
        temp_output_dict['Related_Companies'] = master_input_dict[key]['Related companies'].strip()
        temp_output_dict['Related_Individuals'] = master_input_dict[key]['Related individuals'].strip()
        
        temp_output_dict['Further Information'] = master_input_dict[key]['Further Information'].strip()
        
        ###### folder path where the extractred reports get written.
        report_path = cf.cl_txt_files_path
        organisation = org_name1
        organisation = organisation + '_' + key + '.txt'
        file_path = os.path.join(report_path, organisation)
        temp_output_dict['File Path'] = file_path
        # final_output[key] = lst
        temp_output_dict1 = copy.deepcopy(temp_output_dict)
        del temp_output_dict1['Further Information']
        final_output1[key] = temp_output_dict1
        final_output[key] = temp_output_dict               
                        
    # final_output[key] = lst
    # org_name = 'xyz'
    # org_name1 = org_name       
    print('writing file-----------------------------')
    if(final_output != []):
        for key in final_output.keys():
            temp_report = final_output[key]
            # temp_report = ' '.join(temp_report)
            # report_path = r'C:\Users\sraza12\Desktop\CL screening\CL screening text1'
            report_path = cf.cl_txt_files_path
            temp_org_name = org_name1
            # temp_org_name = temp_org_name + '_' + key + key +'.txt'
            temp_org_name = temp_org_name + '_' + key + '.json'
            path = os.path.join(report_path, temp_org_name)
            print(path)
            # with open(path, 'w', encoding = 'utf-8') as fw:
                # fw.write(temp_report)
            with open(path, "w") as write_file:
                json.dump(temp_report, write_file)

## with open(r'C:\Users\sraza12\Desktop\CL screening\CL screening text1\6 CL_Prudential_Hit1.json') as f:
#    # x = json.loads(f.read())