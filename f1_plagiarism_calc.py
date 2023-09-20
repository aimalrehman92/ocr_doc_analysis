
#####################################################################################################################
# This flask application for Plagiarism calculation
# This application can process image, text files and extract text
# For similarity measure, we are relying on cosine similarity coefficient and interpret it as percentage similarity
#####################################################################################################################

from alivia_text_library import extract_text_from_image, extract_text_from_doc
from alivia_process_files import process_attachments
from alivia_stats_lib import plagiarism_calculation
from flask import Flask, request, jsonify

app = Flask(__name__)
app.json.sort_keys = False

@app.route('/plagiarism_calculation', methods=['GET', 'POST'])
def main():

    if request.method == "GET":
        
        return jsonify({"response":"This is an OCR based plagiarism checking application. Welcome !!!"})

    elif request.method == "POST":
        req_json = request.json
        attachments_len = len(req_json)
        
        dummy_output = {"primary_output":{"Attach_None":["NA"]}, "secondary_output": {"Attach_None": "NA"}} # Placeholder!
    
        if attachments_len <= 1:
            output = dummy_output

        else:
            proc_attach = process_attachments()
            extract_from_image = extract_text_from_image()
            extract_from_doc = extract_text_from_doc()
            plag_calc = plagiarism_calculation()

            list_paths, list_texts = [], [] 

            for ii in range(1, attachments_len+1): 
                list_paths.append(req_json[str(ii)])
            
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
            
            print("*****************")
            print(output)
            print("*****************")

        return jsonify(output)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)

            
            