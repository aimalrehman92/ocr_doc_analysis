
####

from utilities import extract_text_from_image, extract_text_from_doc, extract_text_from_table
from utilities import plagiarism_calculation
from utilities import process_attachments, plagiarism_calculation
from flask import Flask, request, jsonify

def main_plagiarism_check(req_input, request="POST"):

    if request == "GET":
        return jsonify({"response":"This is an OCR based plagiarism checking application. Welcome !!!"})

    elif request == "POST":
        req_json = req_input
        attachments_len = len(req_json)
        
        #print("LET US CHECK THE LENGTH: ", attachments_len)
        dummy_output = {"primary_output":{"Attach_None":["NA"]}, "secondary_output": {"Attach_None": "NA"}} # Placeholder!

        if attachments_len <= 1:
            output = dummy_output
        
        else:
            
            list_paths = []
    
            for ii in range(1, attachments_len+1): 
                list_paths.append(req_json[str(ii)])

            process_obj = process_attachments()
            list_types, index_types = process_obj.group_similar_file_types(list_paths)
            #print(index_types)
            list_ocr_texts, list_doc_texts, list_table_texts = [], [], []

            #if len(list_types[0]) != 0:
                #extract_text_table = extract_text_from_table()
                #list_table_texts = extract_text_table.extract_text(list_types[0])
                #list_table_texts = extract_text_table.process_all_text(list_table_texts)
    
            if len(list_types[1]) != 0:
                extract_text_image = extract_text_from_image()
                list_ocr_texts = extract_text_image.extract_text(list_types[1])
                list_ocr_texts = extract_text_image.process_all_text(list_ocr_texts)

            if len(list_types[2]) != 0:
                extract_text_doc = extract_text_from_doc()
                list_doc_texts = extract_text_doc.extract_text(list_types[2])
                list_doc_texts = extract_text_doc.process_all_text(list_doc_texts)

            plag_calc = plagiarism_calculation()
            
            output = plag_calc.similarity_score_all_types(list_ocr_texts, list_doc_texts, list_table_texts, index_types)

            if len(output) > 1:
                #output = plag_calc.filter_top_sim_score(output)
                output = plag_calc.filter_matrix(output)
            else:
                output = dummy_output
                
        return output


if __name__ == '__main__':

    
    #req_input = {"1" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\Data_for_demo\\Fausto_Alber_1.jpg",
    #"2" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\Data_for_demo\\Fausto_alber_genuine_pdf.pdf"   
#}

    req_input =  {"1" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\OCR_Tahira\\Text 1.docx",
    "2" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\OCR_Tahira\\Text 2.docx",
    "3" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\OCR_Tahira\\Pres 1.jpg",
    "4" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\OCR_Tahira\\Pres 2.jpg",
    "5" : "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\OCR_Tahira\\Prescription 1.jpg"
    }

    final_out = main_plagiarism_check(req_input, request="POST")

    print(final_out)
