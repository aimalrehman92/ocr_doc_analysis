
from app.src.modules.alivia_text_image_library import ExtractImageText, ExtractDocumentText
from app.src.modules.alivia_process_files import ProcessAttachments, HandleErrorLogs

import os
import numpy as np
import torch
from transformers import RobertaForSequenceClassification, RobertaTokenizer


def load_model(model_path):
    # Load the tokenizer and model from the "roberta-base" pre-trained model
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    #model = RobertaForSequenceClassification.from_pretrained("roberta-base").cuda() # Aimal
    model = RobertaForSequenceClassification.from_pretrained("roberta-base")

    # Load the saved state dict of the fine-tuned model
    model.load_state_dict(torch.load(model_path))

    return tokenizer, model


def preprocess_text(tokenizer, input_text, max_length):
    # Tokenize the input text using the tokenizer
    inputs = tokenizer.encode_plus(
        input_text,
        add_special_tokens=True,
        return_tensors="pt",
        max_length=max_length,
        truncation=True,
    )

    # Get the input_ids and attention_mask tensors
    return inputs["input_ids"], inputs["attention_mask"]
    #return inputs["input_ids"].cuda(), inputs["attention_mask"].cuda() # Aimal


def get_prediction(model, input_ids, attention_mask):
    # Get the predicted label using the input_ids and attention_mask
    outputs = model(input_ids, attention_mask=attention_mask)
    predicted_label = np.argmax(outputs.logits.detach().cpu().numpy())
    return predicted_label


from flask import request, jsonify
from app.src.f1_plagiarism_calc import app
app.json.sort_keys = False

@app.route('/ai_polish_calculator', methods=['GET', 'POST'])
def main_AI_polish_calculator():

    if request.method == "GET":
        
        return jsonify({"response":"This is an OCR based AI Polish Ratio Calculator. Welcome !!!"})

    elif request.method == "POST":

        handle_error = HandleErrorLogs()
    
        try:

            print(" **** API triggered for calculating probability of AI involvement in documents **** ")

            req_json = request.json
            attachments_len = len(req_json)
        
            dummy_output = ['NA']

            if attachments_len <= 1:
                output = dummy_output
            
            else:
                
                model_path = f"{os.getcwd()}\\app\\src\\f3_models\\best_model.pt"
                tokenizer, model = load_model(model_path)
            
                proc_attach = ProcessAttachments()
                extract_from_image = ExtractImageText()
                extract_from_doc = ExtractDocumentText()

                list_paths, list_texts = [], [] 

                for ii in range(1, attachments_len+1): 
                    list_paths.append(req_json[str(ii)])
                
                list_paths = [path_ for path_ in list_paths if path_ is not None] # None cleaning

                for path in list_paths:
                    
                    if proc_attach.detect_file_type(path) == "Image Data":
                        text = extract_from_image.extract_text(path)
                        text = text.splitlines()
                        #text = extract_from_image.process_single_string(text)
                    
                    elif proc_attach.detect_file_type(path) == "Text Data":
                        text = extract_from_doc.extract_text(path)
                        text = text.splitlines()
                        #text = extract_from_doc.process_single_string(text)
        
                    else:
                        pass
                    
                    list_texts.append(text) # list of 'str'

                output = {}
                

                for i in range(attachments_len):
    
                    lines_count, predicted_labels = 0, 0
                    
                    lines = list_texts[i]
                 
                    for line in lines:
                        
                        test_sentence = line.strip()

                        input_ids, attention_mask = preprocess_text(tokenizer, test_sentence, max_length=512)
                        predicted_label = get_prediction(model, input_ids, attention_mask)

                        predicted_labels += predicted_label
                        lines_count += 1

                    polish_ratio = round(predicted_labels/(lines_count+1)*100, 2)
                
                    print(f"ChatGPT polish ratio for attachment at {i}: {polish_ratio}")

                    path = list_paths[i]
                    filename = os.path.basename(path)
                    #output[f"Attach_{i+1}"] = polish_ratio
                    output[filename] = polish_ratio
                    

        except Exception as e:
            handle_error.log_error("logs_ai_checker.txt", e)

        
        return jsonify(output)

    
   
#if __name__ == '__main__':
    #main_AI_polish_calculator()
    #app.run(host='0.0.0.0', port=5030, debug=True)
