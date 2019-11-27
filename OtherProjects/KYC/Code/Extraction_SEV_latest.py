# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 18:17:17 2018

@author: sraza12
"""

from __future__ import division
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
from pdfminer.layout import LAParams
import pandas as pd
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
from pdfminer.pdfdevice import PDFDevice
from sklearn.cluster import KMeans
from os.path import basename
import re
from PyPDF2 import PdfFileReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1
import os
import copy
import config_file as cf
import shutil
import traceback
import json

shutil.rmtree(cf.sev_txt_files_path)
os.mkdir(cf.sev_txt_files_path)                 
##### Pdf folder location 

sev_folder = cf.sev_folder_path
folders = os.listdir(sev_folder)
flag = True
for entity_type in folders:
    print(entity_type)
    folder_path = os.path.join(sev_folder, entity_type)
#folder_path = r'../data/pdf_data/sev/pdf_files'
    folder_path_txt = cf.sev_folder_path_txt    
    if flag:
        shutil.rmtree(folder_path_txt)    
        os.mkdir(folder_path_txt)
        flag = False
    folder_list = os.listdir(folder_path)
    for item in folder_list:
        file_name = item.split('.')
        if(len(file_name) == 2):
            file_name = file_name[0]
        elif(len(file_name) > 2):
            file_name = ' '.join(file_name[:len(file_name)-1])
        temp = os.path.join(folder_path, item)
        
        # file = open(os.path.join(folder_path, item), 'rb')
        file = open(temp, 'rb')
        parser = PDFParser(file)
        #document = PDFDocument(parser,password=my_pass)
        document = PDFDocument(parser)
        
        all_tables = list()
        total_pages = resolve1(document.catalog['Pages'])['Count']
        #print('page numbers: ', total_pages)
        # base_filename = basename(example_file)
        base_filename = basename(os.path.join(folder_path, item))
        # print(base_filename)
        bs= base_filename
        #page_number1 = int(input('Enter Page Number: '))
        #page_number = page_number1 - 1
        #base_filename = base_filename.replace('.pdf','') + '_pg_' + str(page_number1)
        f = open('math_log.txt', 'a', encoding='utf-8')
        number_of_clusters_list = []
        
        for page_number in range(0,total_pages):
            try:
                base_filename = base_filename.replace('.pdf', '') + '_pg_' + str(page_number)
                class pdfPositionHandling:
                    xo = list()
                    yo = list()
                    text = list()
                    def parse_obj(self, lt_objs):
            
                        # loop over the object list
                        for obj in lt_objs:
                            if isinstance(obj, pdfminer.layout.LTTextLine):
                                if  'Amount YTD Hrs' in str(obj.get_text()):
                                    pdfPositionHandling.xo.append(int(obj.bbox[0]))
                                    pdfPositionHandling.yo.append(int(obj.bbox[1]))
                                    pdfPositionHandling.text.append('Amount')
            
                                    pdfPositionHandling.xo.append(int(obj.bbox[0])+40)
                                    pdfPositionHandling.yo.append(int(obj.bbox[1]))
                                    pdfPositionHandling.text.append('YTD Hrs')
            
                                if  'QTYTOTAL' in str(obj.get_text()):
                                    pdfPositionHandling.xo.append(int(obj.bbox[0]))
                                    pdfPositionHandling.yo.append(int(obj.bbox[1]))
                                    pdfPositionHandling.text.append('Amount')
            
                                    pdfPositionHandling.xo.append(int(obj.bbox[0])+40)
                                    pdfPositionHandling.yo.append(int(obj.bbox[1]))
                                    pdfPositionHandling.text.append('YTD Hrs')
            
                                else:
                                    pdfPositionHandling.xo.append(int(obj.bbox[0]))
                                    pdfPositionHandling.yo.append(int(obj.bbox[1]))
                                    # temp = obj.get_text()
                                    # temp = str(temp) + str('$$$')
                                    # pdfPositionHandling.text.append(temp)
                                    pdfPositionHandling.text.append(str(obj.get_text() + ' '))
            
                                #print ("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_')))
                                math_log = str(obj.bbox[0]) + ' ' + str(obj.bbox[1]) + ' ' + str(obj.get_text().replace('\n', '_'))
                                f.write(math_log + '\n')
                            # if it's a textbox, also recurse
            
                            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                                self.parse_obj(obj._objs)
            
                            # if it's a container, recurse
                            elif isinstance(obj, pdfminer.layout.LTFigure):
                                self.parse_obj(obj._objs)
            
            
            
                    def parsepdf(self, filename, startpage, endpage):
            
                        # Open a PDF file.
                        fp = open(filename, 'rb')
            
                        # Create a PDF parser object associated with the file object.
                        parser = PDFParser(fp)
            
                        # Create a PDF document object that stores the document structure.
                        # Password for initialization as 2nd parameter
                        document = PDFDocument(parser)
            
            
                        # Check if the document allows text extraction. If not, abort.
                        if not document.is_extractable:
                            raise PDFTextExtractionNotAllowed
            
                        # Create a PDF resource manager object that stores shared resources.
                        rsrcmgr = PDFResourceManager()
            
                        # Create a PDF device object.
                        device = PDFDevice(rsrcmgr)
            
                        # BEGIN LAYOUT ANALYSIS
                        # Set parameters for analysis.
                        laparams = LAParams()
            
                        # Create a PDF page aggregator object.
                        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            
                            # Create a PDF interpreter object.
                        interpreter = PDFPageInterpreter(rsrcmgr, device)
            
            
                        i = 0
                        # loop over all pages in the document
                        for page in PDFPage.create_pages(document):
                            if i >= startpage and i <= endpage:
                                # read the page into a layout object
                                interpreter.process_page(page)
                                layout = device.get_result()
            
                                # extract text from this object
                                self.parse_obj(layout._objs)
                            i += 1
            
            
                def table_without_border():
                    obj = pdfPositionHandling()
                    obj.parsepdf(r'input_pdf.pdf', 0, 0)
            
                    y0 = pdfPositionHandling.yo
                    x0 = pdfPositionHandling.xo
                    text = pdfPositionHandling.text
            
            
                    from collections import defaultdict
            
                    def list_duplicates(seq):
                        tally = defaultdict(list)
                        for i, item in enumerate(seq):
                            tally[item].append(i)
            
                        return ((key, locs) for key, locs in tally.items())
            
                    rep = list()
                    for each_elem in y0:
                        for each_elem2 in y0:
                            if (math.fabs(each_elem - each_elem2) == 1):
                                rep.append((each_elem, each_elem2))
            
                    for t in rep:
                        for n, i in enumerate(y0):
                            if i == t[0]:
                                y0[n] = t[1]
            
                    l = []
                    for dup in sorted(list_duplicates(y0), reverse=True):
                        l.append(dup)
            
                    table_df = pd.DataFrame([])
                    res_table = list()
                    final_table = list()
                    # temp_text = ''
                    temp_text = ' '
                    final_table2 = list()
            
                    for dup in sorted(list_duplicates(y0), reverse=True):
                        for each_dup in dup[1]:
                            text_append = str(text[each_dup]).replace('\n', '')
                            text_append = text_append
                            # print (text[each_dup],x0[each_dup] ,y0[each_dup])
                            res_table.append(text_append)
            
                        final_table.append(res_table)
            
                        while ' ' in res_table:
                            res_table.remove(' ')
                        while '  ' in res_table:
                            res_table.remove('  ')
                        while '   ' in res_table:
                            res_table.remove('   ')
                        while '$' in res_table:
                            res_table.remove('$')
                        final_table2.append(res_table)
                        res_table = []
            
            
            
                    for each_row in final_table:
                        table_df = table_df.append(pd.Series(each_row), ignore_index=True)
            
            
            
                    s_xo = list(set(x0))
                    s_xo = sorted(s_xo)
            
                    number_of_clusters = len(max(final_table2, key=len))
            
                    if number_of_clusters<18 and number_of_clusters>15:
                        number_of_clusters = 20
            
                    number_of_clusters_list.append(number_of_clusters)
                 #   import math
                    if (int(math.fabs(number_of_clusters_list[0]-number_of_clusters))==1):
                        number_of_clusters = number_of_clusters_list[0]
                    #print(number_of_clusters)
                    import numpy as np
                    kmeans = KMeans(n_clusters=number_of_clusters)
                    arr = np.asarray(x0)
                    arr = arr.reshape(-1, 1)
                    kmeansoutput = kmeans.fit(arr)
                    centroids = kmeansoutput.cluster_centers_
            
                    #centroids = [21, 42, 80, 150, 199, 278, 339, 433, 406,  460, 515, 551]
            
                    new_centroids = list()
                    centroids = centroids.tolist()
                    for each_centroid in centroids:
                        each_centroid = int(each_centroid[0])
                        new_centroids.append(each_centroid)
            
                    new_centroids = sorted(new_centroids)
                    new_centroids = sorted(new_centroids)
                    #print(new_centroids)
                    #new_centroids = [21, 42, 80, 150, 199, 278, 339, 406, 433,  460, 515, 551]
                    #number_of_clusters = number_of_clusters+1
            
            
            
                    rep = list()
                    for each_elem in y0:
                        for each_elem2 in y0:
                            if (math.fabs(each_elem - each_elem2) < 6):
                                rep.append((each_elem, each_elem2))
            
                    for t in rep:
                        for n, i in enumerate(y0):
                            if i == t[0]:
                                y0[n] = t[1]
            
                    l2 = list()
            
                    table_df = pd.DataFrame([])
                    res_table = list()
                    final_table = list()
            
                    for i in range(0, number_of_clusters):
                        res_table.append(' ')
                        l2.append(' ')
            
                    for dup in sorted(list_duplicates(y0), reverse=True):
                        for each_dup in dup[1]:
            
                            text_append = str(text[each_dup]).replace('\n', '')
                            # text_append = text_append.strip()
                            text_append = text_append
                            text_append =  re.sub(' +',' ',text_append)
                            cluster = min(range(len(new_centroids)), key=lambda i: abs(new_centroids[i] - x0[each_dup]))
            
                           # print('clusterr: ', text_append, cluster)
            
                           # print ('res: ', res_table)
                            leading_sp = len(text_append) - len(text_append.lstrip())
                            if (leading_sp>5):
                                text_append = 'my_pdf_dummy' + '          '+text_append
            
            
                            text_append_split = text_append.split('   ')
                            text_append_split_res = []
            
                            for each_ss in text_append_split:
                                if each_ss!='':
                                    each_ss = each_ss.replace('my_pdf_dummy','   ')
                                    text_append_split_res.append(each_ss)
            
                            text_append = text_append.replace('my_pdf_dummy','')
                           # print('tsss: ', text_append_split_res)
            
            
            
                            if (res_table[cluster] != ' ' ):
            
                              #  print ('tt: ', text_append)
                               # print ('tt: ', cluster)
                                app = str(res_table[cluster] + text_append)
            
            
                                res_table[cluster] = app
            
                            #elif(len(text_append_split_res)>1 and res_table[cluster] != ' '):
            
            
            
                            elif(len(text_append_split_res) > 1):
                                ap = cluster
                                for each_ss in text_append_split_res:
            
                                    try:
            
                                        res_table[ap]=each_ss
                                        ap = ap+1
                                    except:
                                        res_table.insert(ap,each_ss)
                                        ap = ap + 1
            
            
                            else:
            
                                res_table[cluster]=text_append
                                #res_table.insert(cluster, text_append)
            
                        for i in range(0, number_of_clusters):
                            res_table.append(' ')
            
                        if not all(' ' == s or s.isspace() for s in res_table):
                            final_table.append(res_table)
                        res_table = []
                        for i in range(0, number_of_clusters):
                            res_table.append(' ')
            
            
                    for each_row in final_table:
                        table_df = table_df.append(pd.Series(each_row), ignore_index=True)
            
            
                    all_tables.append(table_df)
            
            #        writer.save()
            
            
            
                import PyPDF2
            
                #pfr = PyPDF2.PdfFileReader(open(example_file, "rb"))
                pfr = PyPDF2.PdfFileReader(open(temp, "rb"))
                try:
                    pfr.decrypt('')
                except:
                    pass
            
            
                pg9 = pfr.getPage(page_number) #extract pg 8
                writer = PyPDF2.PdfFileWriter() #create PdfFileWriter object
                #add pages
                writer.addPage(pg9)
                NewPDFfilename = "input_pdf.pdf"
                with open(NewPDFfilename, "wb") as outputStream:  # create new PDF
                    writer.write(outputStream)
            
            
                def extract_layout_by_page(pdf_path):
            
                    laparams = LAParams()
            
                    fp = open(pdf_path, 'rb')
                    parser = PDFParser(fp)
                    document = PDFDocument(parser)
            
                    if not document.is_extractable:
                        raise PDFTextExtractionNotAllowed
            
                    rsrcmgr = PDFResourceManager()
                    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
            
                    layouts = []
                    for page in PDFPage.create_pages(document):
                        interpreter.process_page(page)
                        layouts.append(device.get_result())
                    return layouts
            
            
            
                page_layouts = extract_layout_by_page(NewPDFfilename)
            
            
            
                objects_on_page = set(type(o) for o in page_layouts[0])
            
            
            
                TEXT_ELEMENTS = [
                    pdfminer.layout.LTTextBox,
                    pdfminer.layout.LTTextBoxHorizontal,
                    pdfminer.layout.LTTextLine,
                    pdfminer.layout.LTTextLineHorizontal
                ]
            
                def flatten(lst):
                    return [subelem for elem in lst for subelem in elem]
            
            
                def extract_characters(element):
                    if isinstance(element, pdfminer.layout.LTChar):
                        return [element]
            
                    if any(isinstance(element, i) for i in TEXT_ELEMENTS):
                        return flatten([extract_characters(e) for e in element])
            
                    if isinstance(element, list):
                        return flatten([extract_characters(l) for l in element])
            
            
            
                    return []
            
            
                final_result = list()
                current_page = page_layouts[0]
            
                #print('PROCESSING PAGE : ', page_number)
            
                texts = []
                rects = []
            
            
                for e in current_page:
            
                    if isinstance(e, pdfminer.layout.LTTextBoxHorizontal):
                        texts.append(e)
                    elif isinstance(e, pdfminer.layout.LTRect):
                        rects.append(e)
            
            
            
                characters = extract_characters(texts)
            
            
                xmin, ymin, xmax, ymax = current_page.bbox
                size = 6
            
            
            
                def width(rect):
                    x0, y0, x1, y1 = rect.bbox
                    return min(x1 - x0, y1 - y0)
            
            
                def area(rect):
                    x0, y0, x1, y1 = rect.bbox
                    return (x1 - x0) * (y1 - y0)
            
            
                def cast_as_line(rect):
            
                    x0, y0, x1, y1 = rect.bbox
            
                    if x1 - x0 > y1 - y0:
                        return (x0, y0, x1, y0, "H")
                    else:
                        return (x0, y0, x0, y1, "V")
            
            
                lines = [cast_as_line(r) for r in rects
                         if width(r) < 2 and
                         area(r) > 1]
            
            
            
            
                def does_it_intersect(x, xmin, xmax):
                    return (x <= xmax and x >= xmin)
            
            
                def find_bounding_rectangle(x, y, lines):
            
                    v_intersects = [l for l in lines
                                    if l[4] == "V"
                                    and does_it_intersect(y, l[1], l[3])]
            
            
                    h_intersects = [l for l in lines
                                    if l[4] == "H"
                                    and does_it_intersect(x, l[0], l[2])]
            
                    if len(v_intersects) < 2 or len(h_intersects) < 2:
                        return None
            
                    v_left = [v[0] for v in v_intersects
                              if v[0] < x]
            
                    v_right = [v[0] for v in v_intersects
                               if v[0] > x]
            
                    if len(v_left) == 0 or len(v_right) == 0:
                        return None
            
                    x0, x1 = max(v_left), min(v_right)
            
                    h_down = [h[1] for h in h_intersects
                              if h[1] < y]
            
                    h_up = [h[1] for h in h_intersects
                            if h[1] > y]
            
                    if len(h_down) == 0 or len(h_up) == 0:
                        return None
            
                    y0, y1 = max(h_down), min(h_up)
            
                    return (x0, y0, x1, y1)
            
            
            
                from collections import defaultdict
                import math
            
                box_char_dict = {}
            
                for c in characters:
                    bboxes = defaultdict(int)
                    l_x, l_y = c.bbox[0], c.bbox[1]
                    bbox_l = find_bounding_rectangle(l_x, l_y, lines)
                    bboxes[bbox_l] += 1
            
                    c_x, c_y = math.floor((c.bbox[0] + c.bbox[2]) / 2), math.floor((c.bbox[1] + c.bbox[3]) / 2)
                    bbox_c = find_bounding_rectangle(c_x, c_y, lines)
                    bboxes[bbox_c] += 1
            
                    u_x, u_y = c.bbox[2], c.bbox[3]
                    bbox_u = find_bounding_rectangle(u_x, u_y, lines)
                    bboxes[bbox_u] += 1
            
                    if max(bboxes.values()) == 1:
                        bbox = bbox_c
                    else:
                        bbox = max(bboxes.items(), key=lambda x: x[1])[0]
            
                    if bbox is None:
                        continue
            
                    if bbox in box_char_dict.keys():
                        box_char_dict[bbox].append(c)
                        continue
            
                    box_char_dict[bbox] = [c]
            
                for x in range(int(xmin), int(xmax), 10):
                    for y in range(int(ymin), int(ymax), 10):
                        bbox = find_bounding_rectangle(x, y, lines)
            
                        if bbox is None:
                            continue
            
                        if bbox in box_char_dict.keys():
                            continue
            
                        box_char_dict[bbox] = []
            
                def chars_to_string(chars):
            
                    if not chars:
                        return ""
                    rows = sorted(list(set(c.bbox[1] for c in chars)), reverse=True)
                    text = ""
                    for row in rows:
                        sorted_row = sorted([c for c in chars if c.bbox[1] == row], key=lambda c: c.bbox[0])
                        text = text+' '+"".join(c.get_text() for c in sorted_row)
                        # print(text)
                    return text
            
            
                def boxes_to_table(box_record_dict):
            
                    boxes = box_record_dict.keys()
                    rows = sorted(list(set(b[1] for b in boxes)), reverse=True)
                    table = []
                    for row in rows:
                        sorted_row = sorted([b for b in boxes if b[1] == row], key=lambda b: b[0])
                        table.append([chars_to_string(box_record_dict[b]) for b in sorted_row])
                    return table
            
            
            
                result = boxes_to_table(box_char_dict)
                final_result.extend(result)
            
            
                #if (final_result):
                if(False):
                    # print ('Found Table with border')
                    table_df = pd.DataFrame(final_result)
                    all_tables.append(table_df)
            
                else:
                   # print('Looking for Table without border')
                    table_without_border()
            except:
         #   print('i am in except')
                pass
        
        def helper_anomaly(all_tables, col_len):
            all_tables_new = pd.DataFrame([])
            correct = ['Currency:', 'Base       NTD', 'Base        USD', 'NTD']
            final_correct = []
            row_no = 0
            for index, row in all_tables.iterrows():
                if ('BaseBase' in str(row)):
                    try:
                        all_tables.loc[row_no]=(correct)
                    except:
                        for i in range(0, col_len):
                            try:
                                final_correct.append(correct[i])
                            except:
                                final_correct.append(' ')
                        all_tables.loc[row_no] = final_correct
                row_no+=1
            return all_tables
        
        
        
        import numpy as np
        all_table_df = pd.DataFrame([])
        for each_table in all_tables:
            all_table_df = all_table_df.append(each_table,ignore_index=True)
            all_table_df = all_table_df.append(pd.Series([np.nan]), ignore_index=True)
            all_table_df = all_table_df.append(pd.Series([np.nan]), ignore_index=True)
            all_table_df = all_table_df.append(pd.Series([np.nan]), ignore_index=True)
            all_table_df = all_table_df.append(pd.Series([np.nan]), ignore_index=True)
            all_table_df = all_table_df.append(pd.Series([np.nan]), ignore_index=True)
            all_table_df = all_table_df.append(pd.Series([np.nan]), ignore_index=True)
            
        
        try:
            all_tables = helper_anomaly(all_table_df, len(all_table_df.columns.values))
        except:
            pass
            
        # all_table_df.to_csv(r'C:\Users\sraza12\Desktop\CL_doc\Project_KYCD\AIML_data_all\Material\divesh.txt', header=None, index=None,)
        txt_file = entity_type + '_' + file_name.replace('_','-') + '.txt'
        all_table_df.to_csv(os.path.join(folder_path_txt, txt_file), header=None, index=None)
    ################### End of Table Extraction Code ##################    
    
    
    ############# folder path of converted text file.
    ############# Run the code from here in case you have converted text file of pdf.
    ############# Text_folder is the folder location of converted pdf to text files.
text_folder = cf.sev_folder_path_txt
text_folder_list = os.listdir(text_folder)
temp_org_para = []
try:
    for txt_item in text_folder_list:
        txt_item1 = txt_item.split('.')[0]
        text_file = os.path.join(text_folder, txt_item)
        try:
            with open(text_file, 'r') as f:
                txt_file = f.read()            
        except:
            with open(text_file, 'rb') as f:
                txt_file = f.read()
            txt_file = txt_file.decode('utf8').strip()        
        bsr_index = txt_file.find('Background Screening Report')
        if bsr_index > 0:
            txt_file = txt_file[bsr_index:]
        txt_file = txt_file.replace(',', '')
        txt_file = txt_file.replace('"', '')
        txt_file = txt_file.split('\n')        
        txt_file = [itm for itm in txt_file if itm != '']
        txt_file = [itm.strip() for itm in txt_file]        
        ####### Searched for all 'ATC-{6,7} followed by Date and stored the corresponding index in the index_list'###
        index_list = []
        article_date = []
        for i in range(len(txt_file)):
            if(re.search('ATC-\d{6,7} - (?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', txt_file[i], re.I)):
                index_list.append(i)                   
                temp_date = txt_file[i]
                temp_date = temp_date.split('-')
                temp_date = temp_date[-1].strip()                
                article_date.append(temp_date)
        
        ######## article_content is the list that contains all the article including the first page ###
        article_content = []
        for i in range(len(index_list)):
            if(i == 0):
                temp_first = txt_file[:index_list[i]]
                article_content.append(temp_first)
            elif(i == len(index_list) - 1):
                temp = txt_file[index_list[i-1]:index_list[i]]
                temp_last = txt_file[index_list[i]:len(txt_file)-1]
                article_content.append(temp)
                article_content.append(temp_last)
                break
            else:
                temp = txt_file[index_list[i-1] : index_list[i]]
                article_content.append(temp)
        
        ######### article_content1 is the list that contains all the articles without comment part #
        article_content1 = []
        for item in article_content:
            flag = 0
            for i in range(len(item)):
                if(item[i].strip() == 'Comments'):
                    index = i
                    flag = 1
            if(flag == 1):
                item1 = item[:index]
            else:
                item1 = item
            article_content1.append(item1)
        
        ######### article_dict is the dictionary that has key as Article1, Article2 and data corresponding ###
        ######### to it as the value ####
        article_dict = {}    
        for i in range(len(article_content1)):
            key = 'Article' + str(i+1)
            article_dict[key] = article_content1[i]
        
        
        ########## Output_json is the dictionary of dictionaries that has Article and date in it.
        output_json = {}
        for i in range(len(article_content1)-1):
            article_json = {}
            key1 = 'Article' + '_' + str(i+1)
            key2 = 'Article' + str(i+1)
            key3 = 'Article' + str(i+1) + '_' + 'Date'
            article_json[key2] = article_content1[i+1]
            article_json[key3] = article_date[i]
            output_json[key1] = article_json
            
        ######### Below is the code to find out the organisation name #####
        org_name_text = article_dict['Article1']
        for i in range(10):  
            if('Date screened  Report created by' in org_name_text[i]):
                org_inx = i 
                org_name = org_name_text[1:org_inx]
                break
        # print(org_name)
        org_name = ' '.join(org_name)
        org_name = re.sub('SCR-\d+', '', org_name)
        org_name = re.sub('\(.+\)', '', org_name)
        org_name = org_name.strip()

#==============================================================================
#         def unique_list(l):
#             ulist = []
#             [ulist.append(x) for x in l if x not in ulist]
#             return ulist
#         
#         for i in range(20):  
#             # if('Organization Name' in item):
#             if('User entered name variations' in org_name_text[i]):
#                 org_name = org_name_text[i+1]
#                 org_name = ' '.join(unique_list(org_name.split()))
#                 break
#         
#         #*********************************************code here
#     
#         org_name = org_name.replace('Organization Name', '')
#         org_name = org_name.replace('Family name', '')
#         org_name = org_name.replace('Given name', '')
#         org_name = org_name.strip()
#         
#         if('Legal Form' in org_name):
#             org_name = org_name.split('Legal Form')
#             org_name = org_name[0]
#             org_name = org_name.strip()
#         
#==============================================================================
        

        ###### Below is the code to put '.' (dot) after Adverse News if present else after Legal issues,
        ###### if present else after Sensetive Country ###
        
        org_name1 = org_name    
        key_name = list(article_dict.keys())
        if(len(key_name) > 1):
            key_name = key_name[1:]
        try:            
            for i in range(len(key_name)):
                temp = article_dict[key_name[i]]
                temp1 = copy.deepcopy(temp)
                text_temp = []
                # head_temp = temp[1]
                # head_temp = head_temp + '. '
                # print(head_temp)
                # text_temp.extend(['.'])
                temp = ' '.join(temp)
                #print(temp[:100])
                if('ADVERSE NEWS' in temp):
                    temp = temp.split('ADVERSE NEWS')
                    temp = temp[0] + 'ADVERSE NEWS. ' + temp[1]    
                    # temp = temp[1:]
                    # text_temp.append(head_temp)
                    text_temp.append(temp)
                elif('LEGAL ISSUES' in temp):
                    temp = temp.split('LEGAL ISSUES')
                    temp = temp[0] + 'LEGAL ISSUES. ' + temp[1]    
                    # temp = temp[1:]
                    # text_temp.append(head_temp)
                    text_temp.append(temp)
                    # temp = temp1
                    # text_temp.append(temp1)
                elif('SENSITIVE COUNTRY' in temp):
                    temp = temp.split('SENSITIVE COUNTRY')
                    temp = temp[0] + 'SENSITIVE COUNTRY. ' + temp[1]
                    text_temp.append(temp)
                else:
                    temp = temp.split(' ')
                    text_temp.append(temp)
                text_temp = ' '.join(text_temp)
                temp_org_name = org_name1
                org_name = temp_org_name + '_' + txt_item1 + '_' + str(i+1) + '.json'
                
                ###### folder path where the extracted articles get written.
                entity_type = txt_item.split('_')[0]
#                article_path = os.path.join(cf.sev_txt_files_path, entity_type)
                path = os.path.join(cf.sev_txt_files_path, org_name)
                article_json = {}
                article_json['article'] = text_temp
                article_json['entity'] = temp_org_name
                article_json['type'] = entity_type            
                with open(path, 'w') as fw:
                    json.dump(article_json, fw)                    
                
        except Exception as e:
            print('erorr', str(e))       
            print(traceback.format_exc())
except Exception as e:
    print('erorr', str(e))