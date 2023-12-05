# Optical Character Recognition based Plagiarism Detection Module (Demo)

This repository contains two OCR based services:
1. OCR based Plagiarism Calculator
2. OCR based Correspondance Checker

Plagiarism Calculator is python service that runs plagiarism analysis and generates report on the uploaded images and/or text documents. They are expected to be medical records. The goal is to find which medical records are highly plagiarised and hence identify fake or forged records that lead to fraud, waste and abuse of healthcare insurance claims. If an uploaded document is an image, it extracts text using deep learning based optical character recognition technique. If it is a text file, the text content is extracted using basic Python functionality. This application also has the facility to return the plagiarised text highlighted over the documents in pair \
Correspondance Checker checks whether the medical records uploaded by the service provider against a particular claim in a case correspond to that claim or not? For now, it only retrieves the information on member name, date of service, procedure code and procedure description from the uploaded documents and checks (exactly) if it matches with the informatino in that claim in the claims table inside the database.

## How to deploy it on your system from scratch?

- Set up Python 3.9.13 on the system you want to run this set of applications on

&nbsp;
- Git clone this repository in a directory (for example: alivia-ocr)

&nbsp;
- Navigate to that parent directory of "alivia-ocr" created in the previous step and create Python virtual environment with the following command:
    - python -m venv alivia-ocr

&nbsp;
- Navigate inside "alivia-ocr" and activate the environment by running the command:
    - Scripts\Activate

&nbsp;
- Install the dependencies using the commnad:
    - pip install requirements.txt

&nbsp;
- Next, install Tesseract-OCR 5.3.1.20230401 or 5.3.3.20231005 from the link: https://github.com/UB-Mannheim/tesseract/wiki
It is recommended to install it in the following path:
"C:\Program Files\Tesseract-OCR\"
(It will ask for path during installation.Don't worry!)
&nbsp;

- Assuming that the environment is still activate, now run one of the two Flask apps on terminal with commands:
    - flask --app f1_plagiarism_calc.py run --host=0.0.0.0 --port=5000
    - flask --app f2_correspondence_checker.py run --host=0.0.0.0 --port=5020

    The first command is for "Plagiarism Calculator" and the second command is for "Correspondence Checker" application.
    To run both, you have to open two terminals.
&nbsp;

- Remember that plagiarism report can be viewed at http://127.0.0.1:5000/plagiarism_calculation/
- Also, remember that correspondance check can be viewed at http://127.0.0.1:5020//prepay_correspondance_check/

## How to run deployed service manually?

- Open terminal and navigate to the directory of this code ("alivia-ocr")
- Type the command: Scripts\Activate (This will activate the environment)
- Now, type the command: flask --app f1_plagiarism_calc.py run --host=0.0.0.0 --port=5000 (to run the plagiarism calculator) \
OR
- Type the command: flask --app f2_correspondence_checker.py run --host=0.0.0.0 --port=5020 (to run the correspondence checker)

## Brief description about the functionalities

The Prepay Correspondance Checker application can check correpsondance between a claim and multiple medical records uploaded on the provider portal in the Prepay module.

The Plagiarism Calculation Python application can run plagiarism report by receiving mulitple files at the same time including images, and text documents. In future, we plan to support textual content stored in the tabular form as well. For now, the following formats are supported for both applications:
- For documents, it can extract text from the following formats:
['.txt', '.docx']
- For images, it can extract text from the following formats:
['.jpeg', '.jpg', '.png', 'pdf']