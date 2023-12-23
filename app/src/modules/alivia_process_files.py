
# This library contains several file handling functionalities:

from pathlib import Path
from fpdf import FPDF
from docx2pdf import convert
import os
from PIL import Image,ImageFilter
import logging
import pythoncom
from docx import Document, text
import fitz  # PyMuPDF
import subprocess


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
        elif Path(path).suffix in ['.jpeg', '.jpg', '.png', '.pdf']:
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
    
    
    def unoconv_pdf(self, input_file, output_file):
        try:
            subprocess.run(['unoconv', '--output', output_file, '--format', 'pdf', input_file], check=True)
            print(f"Conversion successful: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Conversion failed: {e}")
        

    def handle_encoding_error(self, text):
        
        encodings_to_try = ['latin-1', 'utf-8', 'utf-16', 'utf-32', 'windows-1252'] # their sequence is also important. we might not need all.

        # Handling encoding issues by attempting different encodings
        for encoding in encodings_to_try:
            try:
                text = text.encode(encoding, 'ignore').decode(encoding)
                #break
            except UnicodeEncodeError:
                pass
    
        return text


    def fitz_docx_pdf(self, input_file, output_file):

        pdf_document = fitz.open()

        # Open the DOCX file
        with fitz.open(input_file) as doc:
            pdf_bytes = doc.convert_to_pdf()

            # Add the converted PDF bytes to the PDF document
            pdf_document.insert_pdf(fitz.open(stream=pdf_bytes))

        # Save the PDF document
        pdf_document.save(output_file)
        pdf_document.close()
    


    def docx_to_pdf(self, input_file, output_file):
    
        # Initialize the PDF object
        pdf = FPDF()
        pdf.add_page()
        pdf.set_line_width(0.5)
        #pdf.set_auto_page_break(auto=True, margin=20)
        pdf.set_compression(False)
        pdf.set_font("Arial", size=10)

    
        doc = Document(input_file)
        
        for para in doc.paragraphs:

            text = para.text
            text = self.handle_encoding_error(text)
            text = text.replace('\u2022', '-') # Replace bullet points with hyphens
            pdf.multi_cell(w=0, h=5, txt=text) # write text to PDF
            #pdf.ln() # next line
        
        # Output the PDF to the specified file
        pdf.output(output_file)
        


    def txt_docs_to_pdf(self, input_file, index):

        # Converts a text file or a word document file to PDF to local memory
         
        temp_dir = os.getcwd() + "\\app\\temp_folder\\"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        output_file = temp_dir + f"temp_med_record_{index}.pdf"
    
        if Path(input_file).suffix == '.txt':
            
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", size=11)
            
            with open(input_file, encoding='utf-8') as file:
                lines = file.readlines()
 
            max_length = 100
            for line in lines:
                line_list = []
                                
                line = self.handle_encoding_error(line)
    
                while len(line) >= max_length:
                    line_first, line = line[:max_length], line[max_length:]
                    line_list.append(line_first)
                
                line_list.append(line)

                for i in range(len(line_list)):
                    line_once = line_list[i]
                    #pdf.cell(200, 10, txt=line_once, ln=1)
                    pdf.multi_cell(w=0, h=5, txt=line_once)

            # Output the PDF to the specified path and file
            pdf.output(output_file)
        

        elif Path(input_file).suffix == '.docx':
            
            #pythoncom.CoInitialize()
            #convert(input_file, output_file)
            self.docx_to_pdf(input_file, output_file)
            #self.unoconv_pdf(input_file, output_file)
            #self.fitz_docx_pdf(input_file, output_file)
            
        else:
            pass # handle this very nicely instead of just passing!

        return output_file
    

    def save_temp_images(self, image_numpy, index):
        
        # This function will save image in the local memory for temporary use
        
        temp_dir = os.getcwd() + "\\app\\temp_folder\\"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        temp_path = temp_dir + f"temp_img_{index}.jpg"        
        image = Image.fromarray(image_numpy, "RGB")

        # Define the desired new size (resolution)
        new_width = image.width * 1
        new_height = image.height * 1

        # Resize the image to the new size using the nearest-neighbor resampling method
        upscaled_image = image.resize((new_width, new_height), Image.NEAREST)

        upscaled_image.save(temp_path)

        #dpi = image.info.get("dpi")
        #print("DOTS PER IMAGE: ", dpi)
        #upscaled_image = upscaled_image.filter(ImageFilter.SHARPEN)
        upscaled_image = upscaled_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        #image_size = image_numpy.shape
        image_size = new_width, new_height

        #print("IMAGE SIZE and TYPE", image_size, type(image))
        
        return temp_path, image_size
    

    def images_to_pdf(self, list_numpy_images, index, filepath):

        # This will convert an image or a group of images per attachment to a single PDF in local and return path
        
        temp_dir = os.getcwd() + "\\app\\temp_folder\\"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        directory, filename = self.split_directory_filename(filepath)
        filename = filename + '_highlight.pdf'

        output_pdf_path = directory + '\\' + filename

        pythoncom.CoInitialize()
        
        pdf = FPDF()
        
        for j in range(len(list_numpy_images)):
            
            temp_path, img_size = self.save_temp_images(list_numpy_images[j], j)
            #w, h, c = img_size
            pdf.add_page()
            #pdf.image(temp_path, 10, 10, 180)
            pdf.image(temp_path, 2, 2, 200)

        pdf.output(output_pdf_path)

        del(pdf)

        # To be used by the service outside
        #temp_dir = os.getcwd() + "\\temp_folder\\"
        #output_pdf_path = temp_dir + f"output_{index}.pdf"

        return output_pdf_path
    
    
    def split_directory_filename(self, my_string):
        
        last_index = my_string.rfind('\\')

        if last_index != -1:
            # Extract the substring before the last comma
            directory_info = my_string[:last_index]
            file_name = my_string[last_index + 1:]
            
        else:
            pass # case handle this issue
    
        return directory_info, file_name
            

class HandleErrorLogs:

    def __init__(self):
        pass

    def log_error(self, log_filename, message):

        temp_dir = os.getcwd() + "\\app\\logs\\"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        log_filepath = temp_dir + f"{log_filename}"
        
        logging.basicConfig(filename=log_filepath, filemode='a', format='%(asctime)s - %(message)s', level=logging.ERROR)
        
        with open(log_filepath, "a+") as myfile:
            myfile.write("\n ****************************************************************** \n")
            myfile.write(f'ERROR : {message} \n')
        myfile.close()

        logging.error("Exception occurred", exc_info=True)

