

import os
import numpy as np
import pandas as pd
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
#from nltk.corpus import stopwords
#from nltk.corpus import stopwords.words('english') as stopwords
from nltk.tokenize import word_tokenize,sent_tokenize
from docx import Document
from pdf2image import convert_from_path

from datetime import datetime

############################################# Process attachments #############################################

class process_attachments:

    def __init__(self):
        pass

    def detect_file_type(self, file_path):

        self.file_type = None
        self.path = file_path
        if Path(self.path).suffix in ['.csv', '.xls', '.xlsb', '.xlsm', '.xlsx', '.xml', '.ods']:
            self.file_type = "Tabular Data"
        elif Path(self.path).suffix in ['.jpeg', '.jpg', '.png', '.pdf', '.tiff', '.tif']:
            self.file_type = "Image Data"
        elif Path(self.path).suffix in ['.txt', '.docx']:
            self.file_type = "Text Data"
        else:
            self.file_type = "Junk"
        
        return self.file_type

    def group_similar_file_types(self, list_paths):

        self.list_table_types, self.list_image_types, self.list_text_types = [], [], []
        self.index_table_types, self.index_image_types, self.index_text_types = [], [], [] 
        self.list_path = list_paths
        #for path in list_paths:
        for i in range(len(list_paths)):
            path = list_paths[i]
            self.file_type = self.detect_file_type(path)
            if self.file_type == "Tabular Data":
                self.list_table_types.append(path)
                self.index_table_types.append(str(i+1))
            elif self.file_type == "Image Data":
                self.list_image_types.append(path)
                self.index_image_types.append(str(i+1))
            elif self.file_type == "Text Data":
                self.list_text_types.append(path)
                self.index_text_types.append(str(i+1))
            else:
               pass # discard that document !
        
        return (self.list_table_types, self.list_image_types, self.list_text_types), (self.index_table_types, self.index_image_types, self.index_text_types)
    


