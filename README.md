# Optical Character Recognition based Plagiarism Detection Module (Demo)

This repository contains two OCR based services:
1. OCR based Plagiarism Calculation
2. OCR based Correspondance Checker

Plagiarism Calculation python service runs plagiarism report on the uploaded images and/or text documents. They are expected to be medical records. The goal is to find which medical records are highly plagiarised and hence identify fake or plagiarised medical records that lead to fraud, waste and abuse of healthcare claims. If an uploaded document is an image, it extracts text using deep learning based optical character recognition technique. If it is a text file, the text content is extracted using basic Python functionality. This application also has the facility to return the plagiarised text highlighted over the documents in pair \
Correspondance Checker checks that the medical records uploaded by the service provider against a claim correspond to that claim or not. It retrieves the information on member name, date of service, procedure code and procedure description from the uploaded documents and checks (exactly) if its the same as in the claim obtained from the database.

## How to deploy it on your system from scratch?

- Git clone this repo in a directory
\
&nbsp;
- Navigate to that directory and create Python virtual environment (Python 3.9.13 or 3.9.x) using the following command:
    - python -m venv /path/to/new/virtual/environment 
\
&nbsp;
- Navigate to that directory and activate the environment by running the following command in the terminal
    - Scripts\Activate
\
&nbsp;
- Install the dependencies using the commnad:
    - pip install requirements.txt

In case of any issue, use the following commands to install the modules one by one manually
&nbsp;
- Install the following dependencies:
    - pip install pandas
    - pip install pytesseract
    - pip install nltk
    - pip install pillow
    - pip install textdistance
    - pip install python-docx
    - pip install flask
    - pip install pdf2image
    - pip install pyodbc
    - pip install fpdf
    - pip install docx2pdf
    - pip install pywin32


If installation for any module (e.g. pytesseract) is blocked by CloudFlare, try adding sources to trusted-host, e.g: pip install --trusted-host=pypi.org --trusted-host=files.pythonhosted.org pytesseract
&nbsp;
- Next, install Tesseract-OCR from the link: https://github.com/UB-Mannheim/tesseract/wiki
During installation, it is recommended to install it in the following path:
"C:\Program Files\Tesseract-OCR\"
If a different path is chosen, please note it down and paste it in the script "alivia_text_library" as "self.path_tesseract".
&nbsp;
- Next, install Poppler Release 23.08.0 as a zip file from the link: https://github.com/oschwartz10612/poppler-windows/releases/
It is recommended to unzip it in the following path
"C:\Program Files\"
If a different path is chosen, please note it down and paste it in the script "alivia_text_library" as "self.poppler_path"

- Assuming that the environment is still activate, now run the Flask app on terminal by running any of the two, as desired:
    - flask --app f1_plagiarism_calc.py run --host=0.0.0.0 --port=5000
    - flask --app f2_correpondance_checker.py run --host=0.0.0.0 --port=5020

    The first command is for plagiarism calculation application. The second comand is for correspondance checker in prepay.
&nbsp;
- Remember that plagiarism report can be viewed at http://127.0.0.1:5000/plagiarism_calculation/
- Also, remember that correspondance check can be viewed at http://127.0.0.1:5020//prepay_correspondance_check/

## How to run deployed service manually?

- Open terminal and navigate to the directory of this code
- Type the command: Scripts\Activate (This will activate the environment)
- Now, type the command: flask --app f1_plagiarism_calc.py run --host=0.0.0.0 --port=5000 (to run the plagiarism calculation application) \
OR
- Type the command: flask --app f2_correpondance_checker.py run --host=0.0.0.0 --port=5020 (to run the prepay correspondance checker)

## Brief description about the functionality

### Prepay Correspondance Check

The Prepay Correspondance Checker application can check correpsondance between a claim and multiple medical records uploaded on the provider portal in the Prepay module.

### Plagiarism Calculation

The Plagiarism Calculation Python application can run plagiarism report by receiving mulitple files at the same time including images, and text documents. In future, we plan to support textual content stored in the tabular form as well.
- For documents, it can extract text from the following formats:
['.txt', '.docx']

- For images, it can extract text from the following formats:
['.jpeg', '.jpg', '.png', 'pdf', '.tiff', '.tif'],

Output report consist of 'Primary Output' and Secondary Output'. The Primary Output shows highest similarity and the corresponding document, for each uploaded document. The Secondary Output displays similarity matrix containing percentage similarity for all possible pairs of the documents uploaded.

#### Example Input Backend service

{
"1" : "Data_for_SimilarityDetection/Data_for_demo/Fausto_Alber_1.jpg",
"2" : "Data_for_SimilarityDetection/Urgent_Medical_Record.png",
"3" : "Data_for_SimilarityDetection/George_Lawrence_printed.docx"
}

#### Corresponding Output

{
    "primary_output": [
        [
            "Attach_1",
            "Attach_3",
            90.91
        ],
        [
            "Attach_2",
            "Attach_3",
            57.59
        ],
        [
            "Attach_3",
            "Attach_1",
            90.91
        ]
    ],
    "secondary_output": {
        "Attach_1": [
            100.0,
            57.58,
            90.91
        ],
        "Attach_2": [
            57.58,
            100.0,
            57.59
        ],
        "Attach_3": [
            90.91,
            57.59,
            100.0
        ]
    }
}

