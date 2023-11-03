

from alivia_text_image_library import ExtractImageText, ExtractDocumentText, ReturnImageData
from alivia_process_files import ProcessAttachments, HandleErrorLogs
from alivia_stats_library import PlagiarismCalculation

from flask import Flask, request, jsonify

import pandas as pd
import pyodbc
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
app.json.sort_keys = False

@app.route('/prepay_correspondance_check', methods=['GET', 'POST'])

def main():
    
    if request.method == "GET":
        print('We received a get request !!!')
        return jsonify({"response":"This is OCR-based correspondence checking application in Prepay. Welcome !!!"})

    elif request.method == "POST":
        print('We received a post request !!!')
        handle_error = HandleErrorLogs()
        
        try:
            print("Begin !!!!!")
            req_json = request.json
            
            list_paths = req_json["attachments"]
            
            url = req_json["connectionString"]
            
            # Perform string parsing
            url_parts = url.split(";")
            server = url_parts[0].split(":")[0]
            port = url_parts[0].split(":")[1]
            database = url_parts[1].split("=")[1]
            
            print("Printing the URL parts obtained from the string:")
            print(url, server, port, database)

            # Create the connection string
            conn_str = f'DRIVER={{SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'

            # Establish a connection
            conn = pyodbc.connect(conn_str)

            # Create a cursor
            cursor = conn.cursor()

            claimSeq = req_json["claimSeq"]
            tableName = req_json["tableName"]
            prepay_claimID = req_json["prepayClaimID"]
            
            query = f"SELECT MemberName, ServiceFromDate, ProcedureCode, ProcedureDescription FROM {tableName} WHERE claimSeq = {claimSeq};" # hardcode
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
            values_list = [str(i) for i in values_list] # ensure that they are string type and never None
            
            print("All values:")
            print(values_list)
            
            customer_keys = ['Member Name', 'DOS', 'Procedure Code', 'Procedure Description'] # fixed case for parameters for now
            mechanism_list = ["exact", "exact", "exact", "exact"] # how to treat each parameter

            print("The values extracted from the database")
            print(values_list)

            ### Making objects for the relevant classes in the script ###
            plagiarism_calc = PlagiarismCalculation()
            return_image = ReturnImageData()
            proc_attach = ProcessAttachments()
            extract_from_image = ExtractImageText()
            
            ### Read and collect all the data from the documents stored ###
            list_meta_data, list_image_data, list_text_data = [], [], []
            
            print("Pringting the list of paths received")
            print(list_paths)

            for file_count in range(len(list_paths)):
                
                path = list_paths[file_count]
                print(path)

                if proc_attach.detect_file_type(path) == "Text Data":
                    path = proc_attach.txt_docs_to_pdf(path, file_count)
                    list_paths[file_count] = path
        
                text = extract_from_image.extract_text(path)
                text = extract_from_image.process_single_string(text) # if string cleaning + conversion to list of words

                meta, page_images = extract_from_image.extract_text_with_coordinates(path)
                meta = meta[meta['conf'] > 0]
                    
                list_text_data.append(text)
                list_meta_data.append(meta)
                list_image_data.append(page_images)

            
            ### Using the collected data from the above loop, we will now see:
            # 1. what values are found in each attached document?
            # 2. highlight the text found on the corresponding pages of each document
            # 3. create an outline for the headings/found text in that document
            ###

            print("Printing the lengths of the extracted information")
            print(len(list_text_data), len(list_meta_data), len(list_image_data))

            output_paths = []
            score_dict = {}
            output_objects = []
            
            for file_count in range(len(list_paths)):
                
                text = list_text_data[file_count]
                meta = list_meta_data[file_count]
                image_doc = list_image_data[file_count]

                binary_values = plagiarism_calc.uni_directional_plagiarism(values_list, mechanism_list, text)
                score_dict["Attach_"+str(file_count)] = binary_values

                indices = list(np.where(np.array(binary_values) == 1)[0])

                values_found = [values_list[i] for i in indices]
                keys_found = [customer_keys[i] for i in indices]

                print("File count:", file_count)
                print("values_found", values_found)

                # values_found_lower = [values_found[i].lower() for i in range(len(values_found)) if type(values_found[i]) == 'str']

                list_image_data[file_count] = return_image.highlight_text_on_image(list_meta_data[file_count], values_found, list_image_data[file_count], 1)

                file_with_highlights = proc_attach.images_to_pdf(list_image_data[file_count], 0)
   
                
                text_to_mark = values_found
                
                #image_outline_path = f"{os.getcwd()}\\temp_folder\\output_outline_{file_count}.pdf"
                #image_outline_path = f"C:\\Case_Files\\{prepay_claimID}\\output_outline_{file_count}.pdf"
                
                parent_path = 'E:\\CaseFiles'
                final_path = parent_path + f"\\{str(prepay_claimID)}"
                if not os.path.exists(final_path):
                    os.makedirs(final_path)
                file_name = f"output_outline_{file_count}.pdf"
                image_outline_path = f"{final_path}\\{file_name}"

                return_image.create_outline(file_with_highlights, text, meta, text_to_mark, keys_found, image_outline_path)
                
                print("File created with outlines:")
                print(image_outline_path)

                #output_paths.append(image_outline_path)
                file_object = {}
                file_object["claimId"] = prepay_claimID
                file_object["fileLocation"] = file_name
                file_object["fileName"] = file_name
                file_object["fileExtension"] = "PDF"
                file_object["createdOn"] = datetime.today().strftime('%m/%d/%Y')

                output_objects.append(file_object)
    
            df = pd.DataFrame()
            df['parameter'] = customer_keys

            for key in score_dict.keys():
                df[key] =score_dict[key]

            df['results'] = df.iloc[:, 1:].max(axis=1)

            df = df.set_index('parameter')  # Set 'parameter' column as the index
            df['results'] = df['results'].astype('bool')  # Convert results to strings

            # Convert the DataFrame to a dictionary with 'results' as values

            output_binary_decision = df['results'].to_dict()

            output = {"data": output_binary_decision, "pointers": output_objects}
        
            print("Final output:")
            print(output)

        except Exception as e:
            handle_error.log_error("logs_correspondence_app.txt", e)
        
        return jsonify(output)
        


if __name__ == '__main__':
    #main()
    app.run(host='0.0.0.0', port=5020, debug=True)