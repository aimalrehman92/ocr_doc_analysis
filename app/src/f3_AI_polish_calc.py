
from app.src.modules.alivia_text_image_library import ExtractImageText, ExtractDocumentText
from app.src.modules.alivia_process_files import ProcessAttachments, HandleErrorLogs

import os
import numpy as np
import torch
from transformers import RobertaForSequenceClassification, RobertaTokenizer

# function to load a pre-trained model
def load_model(model_path):
    
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    model = RobertaForSequenceClassification.from_pretrained("roberta-base")
    model.load_state_dict(torch.load(model_path))

    return tokenizer, model

# function to preprocess text (tokenization)
def preprocess_text(tokenizer, input_text, max_length):
    # Tokenize the input text using the tokenizer
    inputs = tokenizer.encode_plus(
        input_text,
        add_special_tokens=True,
        return_tensors="pt",
        max_length=max_length,
        truncation=True,
    )

    return inputs["input_ids"], inputs["attention_mask"]
    
# function to make predictions
def get_prediction(model, input_ids, attention_mask):
    outputs = model(input_ids, attention_mask=attention_mask)
    predicted_label = np.argmax(outputs.logits.detach().cpu().numpy())
    return predicted_label

# Main function to check AI involvement in med records
def main_AI_polish_calculator(req_json):

    handle_error = HandleErrorLogs()
    
    try:

        attachments_len = len(req_json)
        
        dummy_output = ['NA']

        if attachments_len < 1:
            output = dummy_output # dummy output if there is any issue with the input
            
        else:
                
            model_path = f"{os.getcwd()}\\app\\src\\f3_models\\best_model.pt" # path to read model parameters
            tokenizer, model = load_model(model_path)
            
            proc_attach = ProcessAttachments()
            extract_from_doc = ExtractDocumentText()

            settings_ = {'color_to_greyscale':False, 'adjust_dpi':False,
                         'noise_filters':False, 'binarize_image':False,
                         'adjust_image_size':False, 'resize_to_A4':False}
            
            extract_from_image = ExtractImageText(settings_) # text extractor block with settings described above
            

            list_paths, list_texts = [], [] 

            for ii in range(1, attachments_len+1): 
                list_paths.append(req_json[str(ii)])
                
            list_paths = [path_ for path_ in list_paths if path_ is not None] # None cleaning in the list

            for path in list_paths:
                    
                if proc_attach.detect_file_type(path) == "Image Data":
                    text = extract_from_image.extract_text(path) # if image: pass through the OCR engine
                    
                elif proc_attach.detect_file_type(path) == "Text Data":
                    text = extract_from_doc.extract_text(path) # else if docx or text, pass through the python library to communicate with these file types
        
                else:
                    pass
                    
                text = text.splitlines() # split text string into lines
                #text = extract_from_image.process_single_string(text) # if any post-processing is required

                list_texts.append(text) # list of 'str'

            output = {}
        
            for i in range(attachments_len):
    
                lines_count, predicted_labels = 0, 0
                    
                lines = list_texts[i]
                 
                for line in lines: # iteratre over lines in the text
                        
                    test_sentence = line.strip()

                    input_ids, attention_mask = preprocess_text(tokenizer, test_sentence, max_length=512) # pass single line of text to preprocess
                    predicted_label = get_prediction(model, input_ids, attention_mask) # and then here to get the prediction

                    predicted_labels += predicted_label # if the label=1, gets added else 0
                    lines_count += 1 # total lines in the text processed so far !

                polish_ratio = round(predicted_labels/(lines_count+1)*100, 2) # compute the percentage of ai involvement
                
                path = list_paths[i]
                
                filename = os.path.basename(path) # get the filename
                output[filename] = polish_ratio # corresponding percentage involvement

            output = {k: v for k, v in sorted(output.items(), key=lambda item: item[1], reverse=True)} # store in the dictionary
                    
    except Exception as e:
        handle_error.log_error("logs_ai_checker.txt", e)
        
    return output


