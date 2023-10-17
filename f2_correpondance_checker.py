
from alivia_text_image_library import ExtractImageText, ExtractDocumentText
from alivia_process_files import ProcessAttachments
from alivia_stats_library import PlagiarismCalculation
from flask import Flask, request, jsonify

import pandas as pd
import pyodbc

app = Flask(__name__)
app.json.sort_keys = False

@app.route('/prepay_correspondance_check', methods=['GET', 'POST'])


def main():
    
    if request.method == "GET":
        
        return jsonify({"response":"This is prepay OCR application. Welcome !!!"})

    elif request.method == "POST":
        
        req_json = request.json
        
        paths_list = req_json["attachments"]

        dummy_output = {'data': {'Member Name': False, 'DOS': False, 'Procedure Code': False, 'Procedure Description': False}} # Placeholder!
        
        if len(paths_list) < 1:

            output = dummy_output
            print(output)
        
        else:
        
            # IF YOU WANT TO HARD CODE TO RESOLVE BUGS AND ERRORS
            #path_1 = "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\make_believe_medrec.docx"
            #path_2 = "C:\\Users\\MuhammadAimalRehman\\Documents\\OCR_Project\\PyTesseract_Demo_01\\pytesser_demo\\Data_for_SimilarityDetection\\make_believe_medrec.docx"
            #paths_list = [path_1, path_2]

            #########################################################
        
            url = req_json["connectionString"]

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

            claimSeq = req_json["claimSeq"]
            tableName = req_json["tableName"]
            query = f"SELECT MemberName, ServiceToDate, ProcedureCode, ProcedureDescription FROM {tableName} WHERE claimSeq = {claimSeq};"
            cursor.execute(query)
            some_table = cursor.fetchall()
            some_table = pd.DataFrame(some_table)
            some_table = some_table.values[0]
        
            # IF YOU WANT TO HARD CODE TO RESOLVE BUGS AND ERRORS
            #some_table = [["Micheal Oven", "02/12/1992", "AAA", "bla bla bla"]]
            #####################################################

            # Close cursor and connection
            cursor.close()
            conn.close()

            mem_name = some_table[0][0]
            dos = some_table[0][1]
            proc_code = some_table[0][2]
            proc_des = some_table[0][3]

            # mem_name = some_table[some_table['key'] == 'MemberName']['value'].values[0]
            # dos = some_table[some_table['key'] == 'ServiceToDate']['value'].values[0]
            # proc_code = some_table[some_table['key'] == 'ProcedureCode']['value'].values[0]
            # proc_des = some_table[some_table['key'] == 'ProcedureDescription']['value'].values[0]

            values_list = [mem_name, dos, proc_code, proc_des]
            values_list = [str(i) for i in values_list]
            proc_attach = ProcessAttachments()
            extract_from_doc = ExtractDocumentText()
            extract_from_image = ExtractImageText()
            plagiarism_calc = PlagiarismCalculation()

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

            df = df.set_index('parameter')  # Set 'parameter' column as the index
            df['results'] = df['results'].astype('bool')  # Convert results to strings

            # Convert the DataFrame to a dictionary with 'results' as values
            output_data = df['results'].to_dict()

            output = {"data": output_data}
        
            print(output)

        return jsonify(output)


if __name__ == '__main__':
    #main()
    app.run(host='0.0.0.0', port=5020, debug=True)