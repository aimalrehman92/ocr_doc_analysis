

import numpy as np
import pandas as pd
import textdistance

############################################################################################3

class plagiarism_calculation:
    
    def __init__(self):
        pass


    def similarity_score(self, list_w, index_types):

        self.list_w = list_w # ['ocr1', 'text2', 'text1', 'ocr2', 'ocr3', 'ocr4]
        self.index_types = index_types # [1, 2, 3, 4, 5, 6]
        self.scores = {} 
        self.count = len(self.list_w)
        for i in range(self.count):
            key = 'Attach_'+str(self.index_types[i])
            self.scores[key] = [] # placeholder!
            for j in range(self.count):
                cosine_coef = textdistance.cosine(list_w[i], list_w[j])
                perc_dist = round(cosine_coef*100.0, 2)
                #perc_dist = round((math.pi - math.acos(cosine_coef)) * 100 / math.pi, 2)
                self.scores[key].append(perc_dist)
    
        return self.scores

    
    def similarity_score_all_types(self, ocr_texts, doc_texts, table_texts, index_types):
    
        self.ocr_texts_list = ocr_texts
        self.doc_texts_list = doc_texts
        self.table_texts_list = table_texts
        #self.index_types = index_types
        if ((len(self.ocr_texts_list) !=0) or (len(self.doc_texts_list) !=0)) and (len(self.ocr_texts_list)+len(self.doc_texts_list) >= 2):
            self.ocr_texts_list.extend(self.doc_texts_list) # ['ocr1', 'ocr2', 'ocr3', 'ocr4', 'text2', 'text1']
                                                            # ['ocr1', 'text2', 'text1', 'ocr2', 'ocr3', 'ocr4] # POSTMAN
            self.index_types = list(index_types[1])
            self.index_types.extend(list(index_types[2]))   # ['1', '4', '5', '6', '2', '3']
            temp_list = []
            for i in range(len(self.index_types)):
                #indx = self.index_types[i-1]
                index = str(i+1)
                true_index = self.index_types.index(index)
                temp_list.append(self.ocr_texts_list[true_index])
            self.index_types.sort() # [1, 2, 3, 4, 5, 6]
            self.temp_list = temp_list
            self.score_matrix = self.similarity_score(self.temp_list, self.index_types)
        else:
            self.score_matrix = {"Attach_None": "NA"}

        return self.score_matrix
    

    def filter_top_sim_score(self, score_matrix):

        self.doc_names = list(score_matrix.keys()) # [Attach_1, Attach_2, Attach_3, Attach_4, Attach_5, Attach_6]
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


    def filter_matrix(self, score_matrix):
        
        df = pd.DataFrame(columns=list(score_matrix.keys()))
        for key in score_matrix:
            df[key] = score_matrix[key]       
        df = df.T
        df.columns = list(score_matrix.keys())
        df = df.where(np.triu(np.ones(df.shape)).astype(bool))
        df = df.stack().reset_index()
        df.columns = ['doc_1', 'doc_2', 'perc_sim']
        if len(df[df['doc_1'] == df['doc_2']]) < len(df):
            #df = df.drop_duplicates(subset=['Column2'], keep=False)
            df.drop(df[df['doc_1'] == df['doc_2']].index, inplace = True)
            df = df.sort_values(by='perc_sim', ascending=False)
            df.reset_index(drop=True, inplace=True)
        df = df.head(5)
        self.primary_output = df.values.tolist()
        self.final_output = {}
        self.final_output['primary_output'] = self.primary_output
        self.final_output['secondary_output'] = score_matrix

        return self.final_output

        
    def uni_directional_plagiarism(self, set_values, text_bucket):

        score_per_doc = []

        #print("Set of values: ", set_values)
        #print(text_bucket.split())

        member_name, dos, proc_code, proc_des = set_values[0], set_values[1], set_values[2], set_values[3]

        if member_name in text_bucket:
            score_per_doc.append(1)
        else:
            score_per_doc.append(0)
        
        if proc_code in text_bucket:
            score_per_doc.append(1)
        else:
            score_per_doc.append(0)
        
        if proc_des in text_bucket:
            score_per_doc.append(1)
        else:
            score_per_doc.append(0)
        
        if dos in text_bucket:
            score_per_doc.append(1)
        else:
            score_per_doc.append(0)

        #return round(score*100.0/4.0, 2)
        return score_per_doc
    