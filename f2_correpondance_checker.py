


from alivia_text_library import extract_text_from_image, extract_text_from_doc
from alivia_process_files import process_attachments
from alivia_stats_lib import plagiarism_calculation
from flask import Flask, request, jsonify

import pandas as pd
import pyodbc

 
app = Flask(__name__)
app.json.sort_keys = False

@app.route('/prepay_correspondance_check', methods=['GET', 'POST'])


def main():

    #some_table = pd.read_csv("some_table.csv")
    #print(some_table.head()) # MOCK TABLE READ FROM LOCAL FOR PRACTICE

    if request.method == "GET":
        
        return jsonify({"response":"This is prepay OCR application. Welcome !!!"})

    elif request.method == "POST":
        req_json = request.json
        #attachments_len = len(req_json)
        
        paths_list = req_json["attachments"]
        
        #path_1 = "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\make_believe_medrec.docx"
        #path_2 = "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\make_believe_medrec.docx"
        #paths_list = [path_1, path_2]

        #table_name = req_json[""]
        #READ rest of the keys from the input JSON

        url = "localhost:1433;databaseName=ai_analysis;integratedsecurity=true;"

        # Perform string parsing
        url_parts = url.split(";")
        server = url_parts[0].split(":")[0]
        port = url_parts[0].split(":")[1]
        database = url_parts[1].split("=")[1]

        # Create the connection string
        conn_str = f'DRIVER={{SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'

        # Establish a connection
        conn = pyodbc.connect(conn_str)

        # Create a cursor
        cursor = conn.cursor()

        # Example query
        cursor.execute("SELECT * FROM ALIV_MedicalClaimAll where calimSeq = 741988;")
        some_table = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        conn.close()
    
        mem_name = some_table[some_table['key'] == 'Member name']['value'].values[0]
        dos = some_table[some_table['key'] == 'Date of Service']['value'].values[0]
        proc_code = some_table[some_table['key'] == 'Procedure Code']['value'].values[0]
        proc_des = some_table[some_table['key'] == 'Procedure Description']['value'].values[0]

        values_list = [mem_name, dos, proc_code, proc_des]
    
    
        proc_attach = process_attachments()
        extract_from_doc = extract_text_from_doc()
        extract_from_image = extract_text_from_image()
        plagiarism_calc = plagiarism_calculation()

        score_dict = {}
        file_count = 0

        for path in paths_list:
        
            if proc_attach.detect_file_type(path) == "Image Data":
                text = extract_from_image.extract_text(path)
                #text = extract_from_image.process_single_string(text)
                    
            elif proc_attach.detect_file_type(path) == "Text Data":
                text = extract_from_doc.extract_text(path)
                #text = extract_from_doc.process_single_string(text)

            score_dict["Attach_"+str(file_count)] = plagiarism_calc.uni_directional_plagiarism(values_list, text)
        
            file_count += 1
    
    
        #score_dict = pd.DataFrame.from_dict(score_dict)
        #score_dict = score_dict.max(axis=1) # aggregate
    
        df = pd.DataFrame()
        df['parameter'] = ['Member Name', 'DOS','Procedure Code', 'Procedure Description']

        for key in score_dict.keys():
            df[key] =score_dict[key]

        df['results'] = df.iloc[:, 1:].max(axis=1)

        df = df[['parameter', 'results']]

        print(df) # JUST TO BE SURE !!!!
    
        return jsonify(df)


if __name__ == '__main__':
    #main()
    app.run(host='0.0.0.0', port=5000, debug=True)