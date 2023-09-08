
### Improt Modules ###

import os
import numpy as np
from pathlib import Path
import pytesseract
from PIL import Image
from PIL import ImageFilter
#from PIL.ExifTags import TAGS 
import re
import math
import unicodedata
import textdistance
import nltk
from nltk.tokenize import word_tokenize,sent_tokenize
from docx import Document
from abc import abstractmethod
############################################# Classes on text extraction and text processing #############################################

class extract_text_and_process:

    def __init__(self):
        pass
    
    @abstractmethod
    def extract_text(self, list_paths):
        pass

    def unicode_to_ascii(self, s):
        self.s = s
        return ''.join(c for c in unicodedata.normalize('NFD', self.s) if unicodedata.category(c) != 'Mn')

    def text_cleaning(self, w):
        self.w = w
        self.w = self.unicode_to_ascii(self.w)
        self.w = self.w.lower()                        # Lower casing
        self.w = re.sub(' +', ' ', self.w).strip(' ')  # Remove multiple whitespaces, also leading and trailing whitespaces
        self.w = re.sub(r'[^\w\s]','', self.w)          # Remove special characters and punctuation
        #w = re.sub(r"([0-9])", r" ",w)       # Remove Numerical data
        self.w = re.sub("(.)\\1{2,}", "\\1", self.w)   # Remove duplicate characters
        self.words = self.w.split()                  # Tokenization
        #clean_words = [word for word in words if (word not in stopwords_list) and len(word) > 2]
        self.clean_words = [word for word in self.words if len(word) > 2]
        return " ".join(self.clean_words)

    def process_all_text(self, list_w):
        self.list_w = list_w
        self.clean_strings = []
        self.count = len(self.list_w)
        for i in range(self.count):
            self.clean_text = self.text_cleaning(self.list_w[i])
            self.clean_strings.append(self.clean_text)
        return self.clean_strings



class extract_text_from_image(extract_text_and_process):

    def __init__(self):
        pass
    
    def check_and_adjust_dpi(self, img, size_w=600, size_h=600):
        #size = 7016, 4961
        self.img = img
        self.size_w, self.size_h = 600, 600    
        if (self.img.size[0] < self.size_w) and (self.img.size[0] < self.size_h):
            self.img = self.img.resize(self.size_w, self.size_h, Image.LANCZOS)
        return self.img

    def noise_filters(self, img):
        self.img = img
        self.img = self.img.filter(ImageFilter.MinFilter(3)) # Min pix : Be careful in using this !
        return self.img

    def preprocess_image(self, img):
        self.img = img
        self.img = self.check_and_adjust_dpi(self.img) # adjust dots per image
        self.img = self.noise_filters(self.img)
        self.img = self.img.convert('L') # binarize
        return self.img
        
    def extract_text(self, list_paths):   
        self.list_paths = list_paths
        self.count = len(self.list_paths)
        self.list_texts = []
        self.path_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.path_tesseract

        for i in range(self.count):
            self.image = Image.open(self.list_paths[i])
            self.image = self.preprocess_image(self.image)
            self.text = pytesseract.image_to_string(self.image)
            self.list_texts.append(self.text)
        return self.list_texts
    


class extract_text_from_doc(extract_text_and_process):

    def __init__(self):
        pass

    def extract_text(self, list_paths):   
        self.list_paths = list_paths
        self.texts_list = []
        for i in range(len(self.list_paths)):
            self.doc = Document(self.list_paths[i])
            self.string_one_file = ''
            for j in range(len(self.doc.paragraphs)):
                self.string_one_file = self.string_one_file + self.doc.paragraphs[j].text

            self.texts_list.append(self.string_one_file)
             
        return self.texts_list
    


class extract_text_from_table(extract_text_and_process):

    def __init__(self):
        pass

    def extract_text(self, list_paths):
        pass

############################################# Process attachments #############################################

class process_attachments:

    def __init__(self):
        pass

    def detect_file_type(self, file_path):
        self.file_type = None
        self.path = file_path
        if Path(self.path).suffix in ['.csv', '.xls', '.xlsb', '.xlsm', '.xlsx', '.xml', '.ods']:
            self.file_type = "Tabular Data"
        elif Path(self.path).suffix in ['.jpeg', '.jpg', '.png', 'pdf', '.tif', '.tiff']:
            self.file_type = "Image Data"  
        elif Path(self.path).suffix in ['.txt', '.doc', '.docx', '.odt', '.rtf', '.wpd']:
            self.file_type = "Text Data"
        else:
            self.file_type = "Junk"
        return self.file_type

    def group_similar_file_types(self, list_paths):
        self.list_table_types, self.list_image_types, self.list_text_types = [], [], []
        self.list_path = list_paths
        for path in list_paths:
            self.file_type = self.detect_file_type(path)
            if self.file_type == "Tabular Data":
                self.list_table_types.append(path)
            elif self.file_type == "Image Data":
                self.list_image_types.append(path)
            elif self.file_type == "Text Data":
                self.list_text_types.append(path)
            else:
               pass # Do nothing with that document
        return self.list_table_types, self.list_image_types, self.list_text_types
    

############################################# Plagiarism calculation #############################################
    
class plagiarism_calculation:
    
    def __init__(self):
        pass

    '''
    def __init__(self, ocr_texts, doc_texts, table_texts):
        self.ocr_texts_list = ocr_texts
        self.doc_texts_list = doc_texts
        self.table_texts_list = table_texts
    '''

    def similarity_score(self, list_w):
        self.list_w = list_w
        self.count = len(self.list_w)
        self.scores = {}
        
        for i in range(self.count):
            key = 'Attach_'+str(i+1)
            self.scores[key] = []
            for j in range(self.count):
                cosine_coef = textdistance.cosine(list_w[i], list_w[j])
                perc_dist = round((math.pi - math.acos(cosine_coef)) * 100 / math.pi, 2)
                self.scores[key].append(perc_dist)
    
        return self.scores

    
    def similarity_score_all_types(self, ocr_texts, doc_texts, table_texts):
        
        
        self.ocr_texts_list = ocr_texts
        self.doc_texts_list = doc_texts
        self.table_texts_list = table_texts
        
        if (len(self.ocr_texts_list) !=0) or (len(self.doc_texts_list) !=0):
            self.ocr_texts_list.extend(self.doc_texts_list)
            self.score_matrix = self.similarity_score(self.ocr_texts_list)
        
        else:
            self.score_matrix = {"primary_output":{"Attach_None":["NA"]}, "secondary_output": {"Attach_None": "NA"}}

        #self.score_matrix = self.similarity_score(self.ocr_text_list)

        '''
        if len(self.list_table_texts) != 0:
            # concate all the rows into a single dataframe, compute similarity among the rows
            # and then compare each row with the text if there is any
            self.combined_df = pd.DataFrame()

            for table in self.list_table_texts:
                df = pd.read_csv(table)
                self.combined_df = pd.concat([self.combined_df, df])
                #match_rows(combined_df)
        '''
        return self.score_matrix
    

    def filter_top_sim_score(self, score_matrix):
        
        self.doc_names = list(score_matrix.keys())
        self.primary_output = []
        
        for key in score_matrix.keys():

            temp_arr = np.array(score_matrix[key])
            highest = np.partition(temp_arr.flatten(), -2)[-2]
            index = np.where(temp_arr == highest)[0][0]

            temp_list = [key, self.doc_names[index], highest]
            self.primary_output.append(temp_list)

        self.final_output = {}

        self.final_output['primary_output'] = self.primary_output
        self.final_output['secondary_output'] = score_matrix

        return self.final_output


