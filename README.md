# Optical Character Recognition (OCR) based Alivia-Intelligent Document Processing Applications

This repository contains 3 OCR based services:
1. OCR based Plagiarism Calculator
2. OCR based Correspondence Checker
3. OCR based AI-Involvement Checker

Alivia-OCR-application is a python application that provides the following services:
 1) Plagiarism Calculator: that runs similarity analysis on documents and images and generates report on the uploaded items. They are expected to be medical records. The goal is to find which medical records are highly plagiarised and hence identify fake or forged records that lead to fraud, waste and abuse of healthcare insurance claims. If an uploaded document is an image, it extracts text using deep learning based optical character recognition technique. If it is a text file, the text content is extracted using basic Python functionality. This application also has the facility to return the plagiarised text highlighted over the documents in pair.
 2) Correspondance Checker checks whether the medical records uploaded by the service provider against a particular claim in a case correspond to that claim or not? For now, it only retrieves the information on member name, date of service, procedure code and procedure description from the uploaded documents and checks (exactly) if it matches with the informatino in that claim in the claims table inside the database.
 3) AI-Involvement Checker checks how much text content in a document (expected to be a medical record) has AI involvement in a sense that it is generated or refined by AI models like ChatGPT.


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
- Assuming that the environment is still activate, now run the following command:
    - uvicorn app.main:app --host 0.0.0.0 --port 5020 --reload
&nbsp;
- Remember that plagiarism report can be viewed at http://127.0.0.1:5020/plagiarism_calculation/
- Remember that correspondence check can be viewed at http://127.0.0.1:5020//prepay_correspondance_check/
Remember that correspondence check can be viewed at http://127.0.0.1:5020/ai_polish_calculator/

## How to run deployed service manually?

- Open terminal and navigate to the directory of this code ("alivia-ocr")
- Type the command: Scripts\Activate (This will activate the environment)
- Now, type the command: #uvicorn app.main:app --host 0.0.0.0 --port 5020 --reload

## Brief description about the scope

All three Alivia OCR applications can run plagiarism report by receiving mulitple files at the same time including images, and text documents. In future, we plan to support tabular data as well for the analysis. For now, the following formats are supported for all three applications:
- For documents, it can extract text from the following formats:
['.txt', '.docx', '.pdf]
- For images, it can extract text from the following formats:
['.jpeg', '.jpg', '.png']

We expect the application to show high performance for printed text but it can perform "okayish" on handwritten documents too. To achieve high performance in handwritten content, we need to follow the formal process of training the model on the dataset of handwritten medical records.