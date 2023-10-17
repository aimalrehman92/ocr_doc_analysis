
#####################################################################################################################
# This flask application is for plagiarusm calculation among a chunk of medical records.
# This application can process images, PDF and text files.
# For similarity measure, we are relying on cosine similarity coefficient and interpret it as percentage similarity.
# We have two API: one to return a similarity coefficient matrix and the other to return the plagiarised text
# highlighted over a given pair of documents.
#####################################################################################################################

from alivia_text_image_library import ExtractImageText, ExtractDocumentText, ReturnImageData
from alivia_process_files import ProcessAttachments, HandleErrorLogs
from alivia_stats_library import PlagiarismCalculation

from flask import Flask, request, jsonify
app = Flask(__name__)
app.json.sort_keys = False

@app.route('/plagiarism_calculation', methods=['GET', 'POST'])
def main_percentage():

    if request.method == "GET":
        
        return jsonify({"response":"This is an OCR based plagiarism checking application. Welcome !!!"})

    elif request.method == "POST":

        handle_error = HandleErrorLogs()
        
        try:

            print(" **** API triggered for displaying similarity percentage values **** ")

            req_json = request.json
            attachments_len = len(req_json)
        
            dummy_output = {"primary_output":{"Attach_None":["NA"]}, "secondary_output": {"Attach_None": "NA"}} # Placeholder!
    
            if attachments_len <= 1:
                output = dummy_output

            else:
                proc_attach = ProcessAttachments()
                extract_from_image = ExtractImageText()
                extract_from_doc = ExtractDocumentText()
                plag_calc = PlagiarismCalculation()

                list_paths, list_texts = [], [] 

                for ii in range(1, attachments_len+1): 
                    list_paths.append(req_json[str(ii)])
                
                list_paths = [path_ for path_ in list_paths if path_ is not None] # None cleaning

                for path in list_paths:

                    if proc_attach.detect_file_type(path) == "Image Data":
                        text = extract_from_image.extract_text(path)
                        text = extract_from_image.process_single_string(text)
                    
                    elif proc_attach.detect_file_type(path) == "Text Data":
                        text = extract_from_doc.extract_text(path)
                        text = extract_from_doc.process_single_string(text)
        
                    else:
                        pass
                
                    list_texts.append(text)
            
                indices = list(range(1, len(list_texts)+1))  
                sim_matrix = plag_calc.similarity_score(list_texts, indices)
                output = plag_calc.filter_matrix(sim_matrix)
                output['paths_matrix'] = plag_calc.paths_matrix(list_paths)

                print("******************")
                print(output)
                print("******************")

        except Exception as e:
            handle_error.log_error("logs_plagiarism_application.txt", e)
            
        return jsonify(output)


@app.route('/return_plagiarism_text', methods=['GET', 'POST'])
def main_text_return():

    if request.method == "GET":
        
        return jsonify({"response":"This is an OCR application to return plagiarised text. Welcome !!!"})

    elif request.method == "POST":
        
        handle_error = HandleErrorLogs()

        try:
            
            print(" **** API triggered for displaying plagiarised text between a pair of documents **** ")

            req_json = request.json
            attachments_len = len(req_json)
        
            list_paths = []

            return_image = ReturnImageData()
            proc_attach = ProcessAttachments()
            extract_from_image = ExtractImageText()
            
            image = return_image.null_image((256, 256, 3))
            dummy_output = {"Doc_1": image, "Doc_2": image} # Placeholder!

            if attachments_len != 2:
            
                output = dummy_output

            else:

                list_paths = []

                for i in range(1, attachments_len+1): 
                    list_paths.append(req_json[str(i)])
            
                list_paths = [path_ for path_ in list_paths if path_ is not None] # None cleaning
                
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
                    
                if not ((attachments_len == len(list_text_data)) and (attachments_len == len(list_meta_data)) and (attachments_len == len(list_image_data))):
                    pass
                
                else:

                    common_words = [i for i in list_text_data[0] if i in list_text_data[1]]        
                    common_words = [word for word in common_words if word]
                            
                    for i in range(attachments_len):

                        list_image_data[i] = return_image.highlight_text_on_image(list_meta_data[i], common_words, list_image_data[i], i)

                    output_paths = []
                    
                    for i in range(attachments_len):
                        output_paths.append(proc_attach.images_to_pdf(list_image_data[i], i))

                output = {"1": output_paths[0], "2":output_paths[1]}

                print("*****************")
                print(output)
                print("*****************")
      
        except Exception as e:
            handle_error.log_error("logs_plagiarism_application.txt", e)

    return jsonify(output)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)

