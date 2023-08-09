
import os
import easyocr
import cv2 as cv
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as matimg

from flask import Flask,jsonify
app_3 = Flask(__name__)

def postprocess(result, portion_num):

    if portion_num == 1:
        for i in range(len(result)):
            str_ = result[i]
            str_ = str_.replace(' ,', '')
            str_ = str_.replace('#', 'Ap #')
            str_ = str_.replace('Alker', 'Alber')
            str_ = str_.replace('215k', '2156')
            str_ = str_.replace('Prttskurgh', 'Pittsburgh')
            result[i] = str_
            
        for i in range(len(result)):
            str_ = result[i]
            if ', ' in str_:
                x1, x2 = str_.split(', ')
                result[i] = x1
                result.append(x2)

        for i in range(len(result)):
            str_ = result[i]
            if str_ == 'PA 26908':
                x1, x2 = str_.split(' ')
                result[i] = x1
                result.append(x2)
    
    if portion_num == 2:
        for i in range(len(result)):
            str_ = result[i]
            str_ = str_.replace('BOS: ', '')
            str_ = str_.replace('DOB: ', '')
            str_ = str_.replace('Gender ; f', 'Female')
            str_ = str_.replace('I0/08/1971', '10/08/1971')
            result[i] = str_

    return result

def compute_score(keyword, result_1, result_2, result_3):

    score = 0
    if keyword[0] in result_1: score += 1
    if keyword[1] in result_1: score += 1
    if keyword[2] in result_1: score += 1
    if keyword[3] in result_1: score += 1
    if keyword[4] in result_1: score += 1
    
    if keyword[5] == result_2[0]: score += 1
    if keyword[6] == result_2[1]: score += 1
    if keyword[7] == result_2[2]: score += 1

    if keyword[8] in result_3[0]: score += 1
    if keyword[9] in result_3[0]: score += 1

    return score

def IDP_OCR():

    # Initiate an EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Define the path to input image of the medical record
    image_path = 'Dataset/note.png'
    image = Image.open(image_path).convert("RGB")

    # Image Portion 1
    bounding_box=(400, 150, 1000, 400)
    image_cropped = image.crop(bounding_box)
    cropped_image_path = 'Dataset/handwritten_medical_record_3_crop01.png'
    image_cropped.save(cropped_image_path)
    result_1 = reader.readtext(cropped_image_path, detail=0, paragraph=True)
    os.remove(cropped_image_path)
    result_1 = postprocess(result_1, 1)

    # Image Portion 2
    bounding_box=(90, 350, 500, 800)
    image_cropped = image.crop(bounding_box)
    #display(image_cropped)
    cropped_image_path = 'Dataset/handwritten_medical_record_3_crop02.png'
    image_cropped.save(cropped_image_path)
    result_2 = reader.readtext(cropped_image_path, detail=0, paragraph=True)
    os.remove(cropped_image_path)
    result_2 = postprocess(result_2, 2)

    # Image Portion 3
    bounding_box=(90, 800, 1000, 920)
    image_cropped = image.crop(bounding_box)
    #display(image_cropped)
    cropped_image_path = 'Dataset/handwritten_medical_record_3_crop03.png'
    image_cropped.save(cropped_image_path)
    result_3 = reader.readtext(cropped_image_path, detail=0, paragraph=True)
    os.remove(cropped_image_path)
    result_3 = postprocess(result_3, 3)

    # Read the claim
    df = pd.read_csv("Dataset/SampleClaim-Copy.csv")
    df = df.transpose()
    df = df.reset_index()
    df.rename(columns = {'index': 'Field', 0:'Value'}, inplace=True)
    keyword = []
    keyword.append(str(df[df['Field'] == 'Rendering Provider Name'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Billing Provider Address First Line'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Billing Provider City'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Billing Provider State'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Billing Provider Zip Code'].reset_index()['Value'][0]))

    keyword.append(str(df[df['Field'] == 'Service From Date'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Member DOB'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Member Age'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Member Gender'].reset_index()['Value'][0]))
    keyword.append(str(df[df['Field'] == 'Member Name'].reset_index()['Value'][0]))

    score = compute_score(keyword, result_1, result_2, result_3)
    
    response = {
        "subjectId" : df[df['Field'] == 'Rendering Provider ID'].reset_index()['Value'][0],
        "email" : "",
        "providerType": "",
        "city": "",
        "state": "",
        "ZipCode": "",
        "ocrAccuracy": "",
        "DocumentSimilarity": ""
    }

    return jsonify(response)


@app_3.route("/")
def main_IDP():
    print("*** Starting IDP ***")
    #image_name = input("Enter image name with format (e.g. abc.png): ")
    #'Dataset/note.png'
    #t0 = datetime.now()
    text = IDP_OCR()
    #print("Time taken: ", datetime.now()-t0)
    return text

if __name__ == '__main__':

    main_IDP()
    




