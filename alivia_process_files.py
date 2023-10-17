
# This library contains several file handling functionalities:
# for example, detecting and changing file format or type and saving files on the local, etc

from pathlib import Path
from fpdf import FPDF
from docx2pdf import convert
import os
from PIL import Image
import logging
import pythoncom
############################################# Process attachments #############################################

class ProcessAttachments:

    def __init__(self):
        pass


    def detect_file_type(self, file_path):

        # Detects if a file type is Image or Text or a Table
        file_type = None
        path = file_path

        if Path(path).suffix in ['.csv', '.xls', '.xlsb', '.xlsm', '.xlsx', '.xml', '.ods']:
            file_type = "Tabular Data"
        elif Path(path).suffix in ['.jpeg', '.jpg', '.png', '.pdf', '.tiff', '.tif']:
            file_type = "Image Data"
        elif Path(path).suffix in ['.txt', '.docx']:
            file_type = "Text Data"
        else:
            file_type = "Junk"
        
        return file_type
    

    def group_similar_file_types(self, list_paths):
        
        # Groups file with similar formats together and returns

        list_table_types, list_image_types, list_text_types = [], [], []
        index_table_types, index_image_types, index_text_types = [], [], [] 
        
        for i in range(len(list_paths)):
            path = list_paths[i]
            
            file_type = self.detect_file_type(path)
            
            if file_type == "Tabular Data":
                list_table_types.append(path)
                index_table_types.append(str(i+1))
            elif file_type == "Image Data":
                list_image_types.append(path)
                index_image_types.append(str(i+1))
            elif file_type == "Text Data":
                list_text_types.append(path)
                index_text_types.append(str(i+1))
            else:
               pass # discard that document !
        
        return (list_table_types, list_image_types, list_text_types), (index_table_types, index_image_types, index_text_types)
    

    def txt_docs_to_pdf(self, input_file, index):

        # Converts a text file or a word document file to PDF to local memory
         
        temp_dir = os.getcwd() + "/temp_folder/"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        output_file = temp_dir + f"temp_med_record_{index}.pdf"
    
        if Path(input_file).suffix == '.txt':
            
            pdf = FPDF()
            pdf.add_page()

            # Set font for the PDF
            pdf.set_font("Arial", size=11)
            # Read the text content from the input file
            with open(input_file, 'r') as file:
                lines = file.readlines()
           
            max_length = 90
            for line in lines:
                line_list = []
                while len(line) >= max_length:
                    line_first, line = line[:max_length], line[max_length:]
                    line_list.append(line_first)
                line_list.append(line)

                for i in range(len(line_list)):
                    line_once = line_list[i]
                    pdf.cell(200, 10, txt=line_once, ln=2)

            # Output the PDF to the specified path and file
            pdf.output(output_file)
        

        elif Path(input_file).suffix == '.docx':
            pythoncom.CoInitialize()
            convert(input_file, output_file)
            
        else:
            pass #handle this very nicely!

        return output_file
    

    def save_temp_images(self, img_numpy, index):
        
        # This function will save image in the local memory for temporary use
        
        temp_dir = os.getcwd() + "/temp_folder/"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_path = temp_dir + f"temp_img_{index}.jpg"
        
        img = Image.fromarray(img_numpy, "RGB")
        img.save(temp_path)
        
        img_size = img_numpy.shape
        
        return temp_path, img_size
    

    def images_to_pdf(self, list_numpy_images, index):

        # This will convert an image or a group of images per attachment to a single PDF in local and return path
        
        temp_dir = os.getcwd() + "/temp_folder/"
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        output_pdf_path = temp_dir + f"output_{index}.pdf"
        
        pythoncom.CoInitialize()
        pdf = FPDF()
        
        for j in range(len(list_numpy_images)):
            print(j)
            temp_path, img_size = self.save_temp_images(list_numpy_images[j], j)
            #w, h, c = img_size
            pdf.add_page()
            pdf.image(temp_path, 10, 10, 180)

        pdf.output(output_pdf_path)

        del(pdf)

        # To be used by the service outside
        temp_dir = os.getcwd() + "\\temp_folder\\"
        output_pdf_path = temp_dir + f"output_{index}.pdf"

        return output_pdf_path


class HandleErrorLogs:

    def __init__(self):
        pass

    def log_error(self, log_filename, message):

        temp_dir = os.getcwd() + "/logs/"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        log_filepath = temp_dir + f"{log_filename}"
        
        logging.basicConfig(filename=log_filepath, filemode='a', format='%(asctime)s - %(message)s', level=logging.ERROR)
        
        with open(log_filepath, "a+") as myfile:
            myfile.write("\n ********************** \n")
            myfile.write(f'ERROR : {message} \n')
        myfile.close()

        logging.error("Exception occurred", exc_info=True)

