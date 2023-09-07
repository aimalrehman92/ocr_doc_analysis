# Optical Character Recognition based Plagiarism Detection Module (Demo)

This Python service runs plagiarism report on the uploaded images and/or text documents. If an uploaded document is an image, it extracts text using Deep Learning based optical character recognition technique. In particular, we are using Google's Tesseract engine to do this job. If it is a text file, the text content is extracted using basic Python functionality.

## How to make it work on your system?

- Create a directory in your local
- Navigate to that directory and create Python virtual environment (Python 3.9.13 or 3.9.x) using the following command:
    - python -m venv /path/to/new/virtual/environment 
\
&nbsp;

- Navigate to that directory and activate the environment by running the following command in the terminal
    - Scripts\Activate
\
&nbsp;

- Install the following dependencies:
    - pip install pandas
    - pip install pytesseract
    - pip install nltk
    - pip install pillow
    - pip install textdistance
    If installation for any module (e.g. pytesseract) is blocked by cloudflare, try adding sources to trusted-host:
    - pip install --trusted-host=pypi.org --trusted-host=files.pythonhosted.org pytesseract
\
&nbsp;

- Now run the Flask app on your local (Server: http://127.0.0.1:5000) by running this command on terminal:
    - flask --app flask_class_plag_calc.py run
\
&nbsp;

- Remember that plagiarism report will be displayed on http://127.0.0.1:5000/plagiarism_calculation/

## Brief description about the functionality

This Python application can run plagiarism report by receiving mulitple files at the same time including images, and text documents. In future, we plan to support textual content stored in the tabular form as well.
- For documents, it can extract text from the following formats:
['.txt', '.doc', '.docx', '.odt', '.rtf', '.wpd']

- For images, it can extract text from the following formats:
['.jpeg', '.jpg', '.png', 'pdf', '.tif', '.tiff']

Output report consist of 'Primary Output' and Secondary Output'. The Primary Output shows highest similarity and the corresponding document, for each uploaded document. The Secondary Output displays similarity matrix containing percentage similarity for all possible pairs of the documents uploaded.

### Example Input

{
"1" : "Data_for_SimilarityDetection/Data_for_demo/Fausto_Alber_1.jpg",
"2" : "Data_for_SimilarityDetection/Urgent_Medical_Record.png",
"3" : "Data_for_SimilarityDetection/George_Lawrence_printed.docx"
}

### Corresponding Output

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

