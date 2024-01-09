
#####################################################################################################################
# This flask application is for plagiarusm calculation among a chunk of medical records.
# This application can process images, PDF and text files.
# For similarity measure, we are relying on cosine similarity coefficient and interpret it as percentage similarity.
# We have two functions: one to return a similarity coefficient matrix and the other to return the plagiarised text
# highlighted over a given pair of documents.
#####################################################################################################################

from app.src.modules.alivia_text_image_library import ExtractImageText, ExtractDocumentText, ReturnImageData
from app.src.modules.alivia_process_files import ProcessAttachments, HandleErrorLogs
from app.src.modules.alivia_stats_library import PlagiarismCalculation

# function to return the similarity percentage matrix
def main_percentage(req_json):
    
    handle_error = HandleErrorLogs()
        
    try:

        attachments_len = len(req_json) # number of attachments
        
        dummy_output = {"primary_output":{"Attach_None":["NA"]}, "secondary_output": {"Attach_None": "NA"}} # Placeholder!
    
        if attachments_len <= 1:
            output = dummy_output # dummy output in case no files are attached
            # case-handle when the input is not valid, return NA matrix

        else:
            
            proc_attach = ProcessAttachments()
            extract_from_doc = ExtractDocumentText()
            plag_calc = PlagiarismCalculation()

            settings_ = {'color_to_greyscale':False, 'adjust_dpi':False, 'noise_filters':False, 'binarize_image':False, 'adjust_image_size':False}
            extract_from_image = ExtractImageText(settings_) # specific settings of objects : make different objects having different settings inside
            

            list_paths, list_texts = [], [] 

            for ii in range(1, attachments_len+1): 
                list_paths.append(req_json[str(ii)])
                
            list_paths = [path_ for path_ in list_paths if path_ is not None] # None-cleaning in the list of paths


            filename_list = []
            
            for path in list_paths:
                        
                if proc_attach.detect_file_type(path) == "Image Data":
                    text = extract_from_image.extract_text(path) # if its image or PDF data pass it through OCR engine
                    
                elif proc_attach.detect_file_type(path) == "Text Data":
                    text = extract_from_doc.extract_text(path) # else, use document interaction libraries to extract text
        
                else:
                    pass #ignore

                text = extract_from_doc.process_single_string(text) # process the extracted text
                
                list_texts.append(text) # append it here!

                _, filename = proc_attach.split_directory_filename(path) # full path -----split----> path minus filename , filename
                filename_list.append(filename) # enlist filenames
            
            indices = list(range(1, len(list_texts)+1)) 
                
            sim_matrix = plag_calc.similarity_score(list_texts, filename_list, indices) # get 2D-matrix containing percentage similarity values
            
            output = plag_calc.filter_matrix(sim_matrix) # pass matrix into filter
                                                         # final output wull be matrix itself and the top-5 pairs in terms of %-values
            
            output['paths_matrix'] = plag_calc.paths_matrix(list_paths) # filepaths corresponding to the 2D matrix obtained

    except Exception as e:
        handle_error.log_error("logs_plagiarism_application.txt", e)
            
    return output

# function to return the PDFs of the documents with text highlighted within
def main_text_return(req_json):
    
    handle_error = HandleErrorLogs()
    
    try:

        attachments_len = len(req_json) # number of attachments : it should always be 2
        
        return_image = ReturnImageData()
            
        image = return_image.null_image((256, 256, 3))
        dummy_output = {"Doc_1": image, "Doc_2": image} # Placeholder!

        if attachments_len != 2:
            output = dummy_output # case-handle, return a pair of white images if the input is invalid

        else:
            
            proc_attach = ProcessAttachments()

            settings_ = {'color_to_greyscale':True, 'adjust_dpi':True,
                         'noise_filters':False, 'binarize_image':False,
                         'adjust_image_size':True, 'resize_to_A4':True}
            
            extract_from_image = ExtractImageText(settings_) # black box with particular settings as written above
        
            list_paths = []

            for i in range(1, attachments_len+1):
                list_paths.append(req_json[str(i)])
            
            list_paths = [path_ for path_ in list_paths if path_ is not None] # None cleaning in the list of paths for the attachments

            list_paths_original = list_paths.copy() # make a copy
                
            list_meta_data, list_image_data, list_text_data = [], [], []

            for attach_no in range(len(list_paths)): # loop over each attachment in the pair
                
                path = list_paths[attach_no] # path string
                
                if proc_attach.detect_file_type(path) == "Text Data":
                    path = proc_attach.txt_docs_to_pdf(path, attach_no) # if it is a text data, convert it into a PDF
                    list_paths[attach_no] = path # replace the original path with the path of the PDF created
                    
                text = extract_from_image.extract_text(path) # if its an image or PDF, pass through OCR pipeline to extract text
                text = extract_from_image.process_single_string(text) # process the obtained text

                meta, page_images = extract_from_image.extract_text_with_coordinates(path) # then also obtain image and meta data of text
                    
                list_text_data.append(text)
                list_meta_data.append(meta) 
                list_image_data.append(page_images) # store in the same sequence as paths
                    
                
            if not ((attachments_len == len(list_text_data)) and (attachments_len == len(list_meta_data)) and (attachments_len == len(list_image_data))):
                #sanity check : if it doesn't hold then return dummpy
                output = dummy_output
                
            else:

                common_words = [i for i in list_text_data[0] if i in list_text_data[1]] # find common words in the pair of attachments 
                common_words = [word for word in common_words if word] # making sure valid strings only
                            
                for i in range(attachments_len):# loop over the two attachments
                    list_image_data[i] = return_image.highlight_text_on_image(list_meta_data[i], common_words, list_image_data[i], i) # return list of images/pages
                                                                                                                                      # in each attachment
                                                                                                                                      # with the common text highlighted on it
                    list_image_data[i] = extract_from_image.postprocess_images(list_image_data[i])                                    # post-process each image in the attachment

                output_paths = []
                    
                for i in range(attachments_len): # loop over the range of attachments
                    output_paths.append(proc_attach.images_to_pdf(list_image_data[i], i, list_paths_original[i])) # convert list of images against each attachment
                                                                                                                  # into a PDF and store in their origin directory

                output = {"1": output_paths[0], "2":output_paths[1]} # return the two PDFs as output to the front-end modal
      
    except Exception as e:
        handle_error.log_error("logs_plagiarism_application.txt", e)

    return output
