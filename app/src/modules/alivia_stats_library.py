

import numpy as np
import pandas as pd
import textdistance

############################################################################################3

class PlagiarismCalculation:
    
    def __init__(self):
        pass # left for future!

    # function to capture similarity score among the bunch of documents
    def similarity_score(self, list_strings, filename_list, index_types):
        # input: list of string values (texts extracted from documents)
            # list of string values (correpsonding filenames in the exact same order)
            # list of index types which is unused 
        #output : dictionary with keys: filenames, values: list of numeric values showing percentage with all files including itself

        scores = {} 
        count = len(list_strings)

        for i in range(count):
            #key = 'Attach_'+str(index_types[i])
            key = filename_list[i] # make key
            scores[key] = [] # placeholder!

            for j in range(count):
                cosine_coef = textdistance.cosine(list_strings[i], list_strings[j]) # compute cosine distance as similarity measure
                perc_dist = round(cosine_coef*100.0, 2)
                #perc_dist = round((math.pi - math.acos(cosine_coef)) * 100 / math.pi, 2)
                scores[key].append(perc_dist)
    
        return scores
    
    # function to store paths information in a matrxi form
    def paths_matrix(self, list_paths):
        # input: list of string values as path of files
        # output : dictionary with keys: filenames, values: list of path strings rotated one by one

        paths_matrix = {}

        for i in range(len(list_paths)):
            
            paths_matrix[list_paths[i]] = []

            for j in range(len(list_paths)):

                paths_matrix[list_paths[i]].append(list_paths[j])

        return paths_matrix

    # Another function to capture similarity score among the bunch of documents (UNUSED)
    def similarity_score_all_types(self, ocr_texts, doc_texts, table_texts, index_types):
        # input: list of texts extracted through OCR pipeline
            # list of texts extracted from docs or text files
            # list of texts extracted from tavles
            # indices of those individual types
        # output : dictionary with keys: Attachment_no, values: list of numeric values showing percentage with all files including itself
        
        
        # ocr_texts : list of texts coming from OCR block
        # doc_texts : list of texts coming from documents / text files
        # table_texts : list of texts coming from tables / DBs

        if ((len(ocr_texts) !=0) or (len(doc_texts) !=0)) and (len(ocr_texts)+len(doc_texts) >= 2):
            ocr_texts.extend(doc_texts)
                                   
            index_types = list(index_types[1])
            index_types.extend(list(index_types[2]))   # ['1', '4', '5', '6', '2', '3']
            temp_list = []
            
            for i in range(len(index_types)):
                index = str(i+1)
                true_index = index_types.index(index)
                temp_list.append(ocr_texts[true_index])
            
            index_types.sort() # [1, 2, 3, 4, 5, 6]
            temp_list = temp_list
            score_matrix = self.similarity_score(temp_list, index_types)
        
        else:
            score_matrix = {"Attach_None": "NA"}

        return score_matrix
    
    # function to filter top similarity scores
    def filter_top_sim_score(self, score_matrix):
        # input: dictionary with keys: filenames, values: list of numeric percentager values
        # output: dictionary containing primary output and secondary output.

        doc_names = list(score_matrix.keys()) # [Attach_1, Attach_2, Attach_3, Attach_4, Attach_5, Attach_6]
        primary_output = []

        for key in score_matrix.keys():
            temp_arr = np.array(score_matrix[key])
            highest = np.partition(temp_arr.flatten(), -2)[-2]
            index = np.where(temp_arr == highest)[0][0]
            temp_list = [key, doc_names[index], highest]
            primary_output.append(temp_list)
        final_output = {}
        final_output['primary_output'] = primary_output
        final_output['secondary_output'] = score_matrix

        return final_output

    # function to filter top similarity scores
    def filter_matrix(self, score_matrix):
        # input: dictionary with keys: filenames, values: list of numeric percentager values
        # output: dictionary containing primary output and secondary output.
        
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
        primary_output = df.values.tolist()
        final_output = {}
        final_output['primary_output'] = primary_output
        final_output['secondary_output'] = score_matrix

        return final_output

    # function to check if certain strings or substrings (values for example) exist in a text     
    def uni_directional_plagiarism(self, set_values, set_mechanism, text_bucket):
        # input: list of string items to look for in a text
        # set mechanism: list of search mechanism for each item in the above list
        # list of words as pool/bucket to look for values in. This is the text extracted usually for a single document and in which you want to search the desired values.
        # output: assign the score_list for the document

        score_per_doc = []
        
        text_bucket = " ".join(text_bucket)

        for i in range(len(set_values)):
            
            if set_mechanism[i] == "exact":

                if set_values[i] in text_bucket:
                    score_per_doc.append(1)
                else:
                    score_per_doc.append(0)
                
            elif set_mechanism[i] == "similar":

                sentence_len = len(set_values[i].split())
                
                if sentence_len == 1:

                    if set_values[i] in text_bucket:
                        score_per_doc.append(1)
                    else:
                        score_per_doc.append(0)
                
                elif sentence_len > 1:
                    
                    temp_list = set_values[i].split()
                    score = 0
                    for word in temp_list:
                        if word in text_bucket:
                            score += 1

                    if score/sentence_len >= 0.5:
                        score_per_doc.append(1)
                    else:
                        score_per_doc.append(0)

                else:
                    score_per_doc.append(0)

        return score_per_doc
            
    
    # This in unused. This should be retired.
    def uni_directional_plagiarism_old(self, set_values, text_bucket):

        score_per_doc = []

        member_name, dos, proc_code, proc_des = set_values[0], set_values[1], set_values[2], set_values[3]

        if member_name in text_bucket:
            score_per_doc.append(1)
        else:
            score_per_doc.append(0)
        
        if dos in text_bucket:
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

        return score_per_doc
    