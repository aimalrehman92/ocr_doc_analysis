

from alivia_text_image_library import ExtractImageText, ExtractDocumentText, ReturnImageData
from alivia_process_files import ProcessAttachments, HandleErrorLogs
from alivia_stats_library import PlagiarismCalculation

from flask import Flask, request, jsonify

import pandas as pd
import pyodbc
import numpy as np
import os

app = Flask(__name__)
app.json.sort_keys = False

@app.route('/prepay_correspondance_check_arizona', methods=['GET', 'POST'])

def main():
    
    if request.method == "GET":
        
        return jsonify({"response":"This is OCR-based correspondence checking application in Prepay. Welcome !!!"})

    elif request.method == "POST":
        
        handle_error = HandleErrorLogs()
        
        try:
            req_json = request.json
        
            list_paths = req_json["attachments"]

            dummy_output = {'data': {'Member Name': False, 'DOS': False, 'Procedure Code': False, 'Procedure Description': False}} # Placeholder !
        
            if len(list_paths) < 1:

                output = dummy_output
                print(output)
        
            else:
        
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
                query = f"SELECT MemberName, ServiceToDate, ProcedureCode, ProcedureDescription FROM {tableName} WHERE claimSeq = {claimSeq};" # hardcode
                cursor.execute(query)
                some_table = cursor.fetchall()
                some_table = pd.DataFrame(some_table)
                some_table = some_table.values[0]
        
                # Close cursor and connection
                cursor.close()
                conn.close()

                mem_name = some_table[0][0]
                dos = some_table[0][1]
                proc_code = some_table[0][2]
                proc_des = some_table[0][3]

                values_list = [mem_name, dos, proc_code, proc_des]
                values_list = [str(i) for i in values_list]

                customer_keys = ['Member name', 'Date of Service', 'Procedure Code', 'Procedure Description']
                mechanism_list = ["exact", "exact", "exact", "exact"]

                plagiarism_calc = PlagiarismCalculation()
                return_image = ReturnImageData()
                proc_attach = ProcessAttachments()
                extract_from_image = ExtractImageText()
                #extract_from_doc = ExtractDocumentText()

                image = return_image.null_image((256, 256, 3))
                dummy_output = {"Doc_1": image, "Doc_2": image} # Placeholder!

                ### Read and collect all the data from the documents stored ###
                list_meta_data, list_image_data, list_text_data = [], [], []

                for attach_no in range(len(list_paths)):
                
                    path = list_paths[attach_no]
                    print(path)

                    if proc_attach.detect_file_type(path) == "Text Data":
                        path = proc_attach.txt_docs_to_pdf(path, attach_no)
                        list_paths[attach_no] = path
        
                    text = extract_from_image.extract_text(path)
                    text = extract_from_image.process_single_string(text) # if string cleaning + conversion to list of words

                    meta, page_images = extract_from_image.extract_text_with_coordinates(path)
                    meta = meta[meta['conf'] > 0]
                    
                    list_text_data.append(text)
                    list_meta_data.append(meta)
                    list_image_data.append(page_images)

            
                ### This section helps computing the correspondence score ###
                output_paths = []
                for file_count in range(len(list_paths)):
                
                    text = list_text_data[file_count]
                    meta = list_meta_data[file_count]
                    image_doc = list_image_data[file_count]

                    print(type(text), type(meta), type(image_doc))
                    #print(text)
                    print(meta.tail(2))
                    #import numpy as np
                    #print(np.array(image_doc).shape)

                    score_dict = {} # for each file
    
                    binary_values = plagiarism_calc.uni_directional_plagiarism(values_list, mechanism_list, text)
                    score_dict["Attach_"+str(file_count)] = binary_values

                    indices = list(np.where(np.array(binary_values) == 1)[0])

                    values_found = [values_list[i] for i in indices]
                    keys_found = [customer_keys[i] for i in indices]

                    print("***************************")
                    print("Values found:", values_found)

                    # values_found_lower = [values_found[i].lower() for i in range(len(values_found)) if type(values_found[i]) == 'str']

                    list_image_data[file_count] = return_image.highlight_text_on_image(list_meta_data[file_count], values_found, list_image_data[file_count], 1)

                    file_with_highlights = proc_attach.images_to_pdf(list_image_data[file_count], 0)
   
                    print("FILE WITH HIGHLIGHTS")
                    # print(file_with_highlights)
                
                    text_to_mark = values_found
                    # output_pdf_file = file_with_highlights
                
                    image_outline_path = f"{os.getcwd()}\\temp_folder\\output_outline_{file_count}.pdf"
                
                    return_image.create_outline(file_with_highlights, text, meta, text_to_mark, keys_found, image_outline_path)

                    output_paths.append(image_outline_path)

    
                df = pd.DataFrame()
                df['parameter'] = customer_keys

                for key in score_dict.keys():
                    df[key] =score_dict[key]

                df['results'] = df.iloc[:, 1:].max(axis=1)

                df = df.set_index('parameter')  # Set 'parameter' column as the index
                df['results'] = df['results'].astype('bool')  # Convert results to strings

                # Convert the DataFrame to a dictionary with 'results' as values

                output_binary_decision = df['results'].to_dict()

                output = {"data": output_binary_decision, "pointers": output_paths}
        
                print(output)

        except Exception as e:
            handle_error.log_error("logs_correspondence_app.txt", e)
        
        return jsonify(output)
        


if __name__ == '__main__':
    #main()
    app.run(host='0.0.0.0', port=5020, debug=True)