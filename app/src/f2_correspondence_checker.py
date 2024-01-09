

from app.src.modules.alivia_text_image_library import ExtractImageText, ReturnImageData
from app.src.modules.alivia_process_files import ProcessAttachments, HandleErrorLogs
from app.src.modules.alivia_stats_library import PlagiarismCalculation

import pandas as pd
import pyodbc
import numpy as np
import os
from datetime import datetime

# function to check correspondence between medical record and claim in claims DB
def main_correspondence(req_json):

    handle_error = HandleErrorLogs()
        
    try:
            
        list_paths = req_json["attachments"]
        list_paths = [path_ for path_ in list_paths if path_ is not None] # None removal
        list_paths_original = list_paths.copy()
            
        url = req_json["connectionString"] # fetch URL from the incoming JSON object

        # Perform URL parsing
        url_parts = url.split(";")
        server = url_parts[0].split(":")[0]
        port = url_parts[0].split(":")[1]
        database = url_parts[1].split("=")[1]
        
        # Create the connection string for with the database
        conn_str = f'DRIVER={{SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;'

        # Establish connection with the database
        conn = pyodbc.connect(conn_str)

        # Create a cursor
        cursor = conn.cursor()

        claimSeq = req_json["claimSeq"] # claimSeq information
        tableName = req_json["tableName"] # tablename of claims
        prepay_claimID = req_json["prepayClaimID"] # claimID


        if "parameters" in req_json:
            cols = req_json["parameters"]
            customer_keys = cols

        else:
            cols = ['MemberName', 'ServiceFromDate', 'ProcedureCode', 'ProcedureDescription']
            customer_keys = ['Member Name', 'DOS', 'Procedure Code', 'Procedure Description'] # default parameters to look for in the med record

        cols_string = ', '.join(cols) # --> Member Name, DOS, Procedure Code, Procedure Description
    
        query = f"SELECT {cols_string} FROM {tableName} WHERE claimSeq = {claimSeq};" # SQL query
        cursor.execute(query)
        some_table = cursor.fetchall()
        some_table = pd.DataFrame(some_table) # extract the table
        some_table = some_table.values[0]
        
        # Close cursor and connection
        cursor.close()
        conn.close()
            
        # Note: convert the following code snippet into a loop: these were hardcoded for the demo
        #{
        mem_name = some_table[0][0]
        dos = some_table[0][1]
        proc_code = some_table[0][2]
        proc_des = some_table[0][3]
        values_list = [mem_name, dos, proc_code, proc_des]
        #}
        values_list = [str(i) for i in values_list] # ensure that they are string type and never None
            
        #customer_keys = ['Member Name', 'DOS', 'Procedure Code', 'Procedure Description'] # fixed case for parameters for now
        #customer_keys = cols
        mechanism_list = ["exact", "exact", "exact", "exact"] # how to treat each parameter : hard-code for now

        ### Making objects for the relevant classes in the script ###
        plagiarism_calc = PlagiarismCalculation()
        return_image = ReturnImageData()
        proc_attach = ProcessAttachments()
        
        settings_ = {'color_to_greyscale':True, 'adjust_dpi':True,
                         'noise_filters':False, 'binarize_image':False,
                         'adjust_image_size':False, 'resize_to_A4':True}
        
        extract_from_image = ExtractImageText(settings_) # make the object with specific settings/operations
            
        ### Read and collect all the data from the documents stored ###
        list_meta_data, list_image_data, list_text_data = [], [], []
            
        
        for file_count in range(len(list_paths)):
            
            path = list_paths[file_count]
            
            if proc_attach.detect_file_type(path) == "Text Data":
                path = proc_attach.txt_docs_to_pdf(path, file_count) # convert text or docs to PDF
                list_paths[file_count] = path
        
            text = extract_from_image.extract_text(path) # extract text
            text = extract_from_image.process_single_string(text) # process the extracted text

            meta, page_images = extract_from_image.extract_text_with_coordinates(path) # extract metadata and images of the pages in a single attachment
            meta = meta[meta['conf'] > 0]
                    
            list_text_data.append(text)
            list_meta_data.append(meta)
            list_image_data.append(page_images) # append all the extractions into a list in the same sequence as the attachments


        output_paths = []
        score_dict = {}
        output_objects = []
            
        for file_count in range(len(list_paths)): # loop over the paths
                
            text = list_text_data[file_count]
            meta = list_meta_data[file_count]
            image_doc = list_image_data[file_count]

            binary_values = plagiarism_calc.uni_directional_plagiarism(values_list, mechanism_list, text) # check if values_list exist in text in mechanism_list ways
            score_dict["Attach_"+str(file_count)] = binary_values # store the binary decision

            indices = list(np.where(np.array(binary_values) == 1)[0])

            values_found = [values_list[i] for i in indices] # values against which the decision is 1
            keys_found = [customer_keys[i] for i in indices] # keys against which the decision is 1 

            list_image_data[file_count] = return_image.highlight_text_on_image(list_meta_data[file_count], values_found, list_image_data[file_count], 1)
            # highlight text on each image/page in the attachment

            file_with_highlights = proc_attach.images_to_pdf(list_image_data[file_count], 0, list_paths[file_count])
            # store them as PDFs
   
            text_to_mark = values_found

            # do a bit of working to create path strings for the PDFs (the files with highlighted text)
            prepay_claimID = str(prepay_claimID)
            parent_path = list_paths_original[file_count].split('\\')[:2]
            parent_path = '\\'.join(parent_path)
            final_path = f"{parent_path}\\{prepay_claimID}"

            if not os.path.exists(final_path):
                os.makedirs(final_path)
                
            file_name = f"{claimSeq}_output_outline_{file_count}.pdf"
            image_outline_path = f"{final_path}\\{file_name}"

            return_image.create_outline(file_with_highlights, text, meta, text_to_mark, keys_found, image_outline_path)
            # this function creates outline in the corresponding PDFs, for the discovered paramters in the medical records
                
            # make file object for that attachment, the object will introduce the following keys
            file_object = {}
            file_object["claimId"] = prepay_claimID
            file_object["fileLocation"] = file_name
            file_object["fileName"] = file_name
            file_object["fileExtension"] = "PDF"
            file_object["createdOn"] = datetime.today().strftime('%m/%d/%Y')

            output_objects.append(file_object)
    
        df = pd.DataFrame()
        df['parameter'] = customer_keys # store customer keys in a dataframe

        for key in score_dict.keys():
            df[key] = score_dict[key] # store decision against parameters

        df['results'] = df.iloc[:, 1:].max(axis=1) # across multiple attachments, take max so if a paramters is found in any document, the decision should be 1

        df = df.set_index('parameter')  # set 'parameter' column as the index
        df['results'] = df['results'].astype('bool')  # Convert results to strings

        # Convert the DataFrame to a dictionary with 'results' as values
        output_binary_decision = df['results'].to_dict()

        output = {"data": output_binary_decision, "pointers": output_objects} # output decision matrix and
                                                                              # paths of the PDF files with highlighted text/values of parameters
        
    except Exception as e:
        
        handle_error.log_error("logs_correspondence_app.txt", e)
        
    return output
        
