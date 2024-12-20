# Optical Character Recognition (OCR) based Document Analysis

This repository contains OCR-based Plagiarism Calculator.

## What is Plagiarism Calculator?
It is an application that runs similarity analysis on documents and images and generates a report on the uploaded items. The goal is to find which pairs of documents are highly plagiarised (or similar) and hence identify fraudulent documents. If an uploaded document is an image, it extracts text using Deep Learning based optical character recognition technique. If it is a text file, the text content is extracted using basic Python text-handling functionalities. This application also has the facility to return the plagiarised text highlighted over the documents in pair.

![Correlation matrix for the uploaded documents](assets/corr_matrix_2.png)

*Figure 1: Correlation matrix for plagiarism detection*

![Highlighted plagiarised text in the documents pair](assets/side_by_side_analysis.png)

*Figure 2: Highlighted plagiarised text for plagiarism analysis*

## How to deploy it on your system from scratch?

- Set up Python 3.9.13 on the system you want to run this set of applications on
&nbsp;
- Git clone this repository in a directory (for example: ocr_analysis)
&nbsp;
- Navigate to the parent directory of "ocr_analysis" created in the previous step and create a Python virtual environment with the following command:
    - python -m venv ocr_analysis
&nbsp;
- Navigate inside "ocr_analysis" and activate the environment by running the command:
    - Scripts\Activate
&nbsp;
- Install the dependencies using the command:
    - pip install requirements.txt
&nbsp;
- Next, install Tesseract-OCR 5.3.1.20230401 or 5.3.3.20231005 from the link: https://github.com/UB-Mannheim/tesseract/wiki \
It is strongly recommended to install it in the path:
"C:\Program Files\Tesseract-OCR\"
&nbsp;
- Then download the zip file of Poppler from the link: https://github.com/oschwartz10612/poppler-windows/releases/tag/v23.08.0-0 \
Unzip it in the relative path:
"/app/src/modules/"
&nbsp;
- Assuming that the environment is activated, now run the following command:
    - uvicorn app.main:app --host give.some.IP.address --port #portnumber --reload
&nbsp;
- Plagiarism calculator app can be accessed at http://give.some.ip.address:#portnumber/plagiarism_calculation/
&nbsp;
- Text highlighter app can be accessed at http://give.some.ip.address:#portnumber/return_plagiarism_text/

## How to run deployed service manually?

- Open the terminal and navigate to the directory of this code ("ocr_analysis")
- Type the command: Scripts\Activate (This will activate the environment)
- Now, type the command: uvicorn app.main:app --host give.some.IP.address --port #portnumber --reload

## Brief description of the scope

The following formats are supported for the plagiarism analysis:
- For documents, it can extract text from the following formats:
['.txt', '.docx', '.pdf]
- For images, it can extract text from the following formats:
['.jpeg', '.jpg', '.png']

Tesseract OCR can work very well for printed as well hand-written English text documents.