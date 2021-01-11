#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 13:03:05 2020

@author: James Ang
"""
from flask import request,flash,redirect
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path 
import os
import sys
import pytesseract
from PIL import Image
import time


def allowed_file(filename, ALLOWED_EXTENSIONS):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#%% Get File
def request_file(PDF_file, dpi):
    
           
    # Store all the pages of the PDF in a variable        
    pages = convert_from_path(PDF_file,
                              dpi=dpi,
                              grayscale=True,
                              thread_count=3,
                              # size=(1600, None),
                              # fmt="jpeg",
                              # output_folder='/home/alfred/uploads2',
                              # use_cropbox=False,
                              )

    return pages

#%% Part #1 - Convert and store images of each page of PDF file
def page2text(PDF_file,pages,dpi,poss_lc_list):
    
    image_counter = 1
           
    for page in pages: 
      
        # Declaring filename for each page of PDF as JPG 
        # For each page, filename will be: 
        # PDF page 1 -> page_1.jpg 
        # PDF page 2 -> page_2.jpg 
        # .... 
        # PDF page n -> page_n.jpg 
        filename = f"page{str(dpi)}_"+str(image_counter)+".jpg"
          
        # Save the image of the page in system 
        page.save(filename, 'JPEG')
      
        # Increment the counter to update filename 
        image_counter = image_counter + 1
    
    #%% Part #2 - Recognizing text from the images using OCR 
    
    # Variable to get count of total number of pages 
    filelimit = image_counter-1
      
    # Creating a text file to write the output 
    outfile = os.path.basename(PDF_file).rstrip('.pdf')+f"{str(dpi)}" +".txt"
      
    # Open the file in append mode so that  
    # All contents of all images are added to the same file 
    f = open(outfile, "w")
    
    if sys.platform == "win32":
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                      
    # Iterate from 1 to total number of pages 
    for i in range(1, filelimit + 1):
      
        # Set filename to recognize text from 
        # Again, these files will be: 
        # page_1.jpg 
        # page_2.jpg 
        # .... 
        # page_n.jpg 
        filename = f"page{str(dpi)}_"+str(i)+".jpg"
                             
        # Recognize the text as string in image using pytesserct 
        # text = str(((pytesseract.image_to_string(thresh, lang='eng',config='--psm 6')))) 
        
        # text = str(((pytesseract.image_to_string(Image.open(filename)))))
        text = str(((pytesseract.image_to_string(Image.open(filename),lang='eng',config='--psm 6')))) 
    
        # if i == 1:
        #     for word in poss_lc_list:
        #         # print(word)
        #         if word.lower() in text.lower():
        #             word_lc = word
        #             # print(f'"{word}" is found in Document')                        
        #             break
        #         else:
        #             word_lc='No synonymous word for "Letter of Credit" found in Document. \
        #             There is possibility that the document is not a Letter of Credit'
        #             # print('No synonymous word for "Letter of Credit" found in Document. Document is possibly not a Letter of Credit')
      
        # The recognized text is stored in variable text 
        # Any string processing may be applied on text 
        # Here, basic formatting has been done: 
        # In many PDFs, at line ending, if a word can't 
        # be written fully, a 'hyphen' is added. 
        # The rest of the word is written in the next line 
        # Eg: This is a sample text this word here GeeksF- 
        # orGeeks is half on first line, remaining on next. 
        # To remove this, we replace every '-\n' to ''. 
        text = text.replace('-\n', '') + '\n' # <-- additional '\n' for extra line between pages
      
        # Finally, write the processed text to the file. 
        f.write(text)
      
    # Close the file after writing all the text. 
    f.close() 
    
    return outfile


def scan_image(filename, word_lc, start_time):

    # Creating a text file to write the output 
    outfile = filename.rstrip('.jpg')+".txt"

    # All contents of all images are added to the same file 
    f = open(outfile, "w")
    

    if sys.platform == "win32":
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = str(((pytesseract.image_to_string(Image.open(filename),lang='eng',config='--psm 6'))))
    
    text = text.replace('-\n', '')

    # Finally, write the processed text to the file. 
    f.write(text)
    f.close()

    print(outfile)


    #%% Timer ends
    time_taken = round(time.time() - start_time,2)

    retJSON = { 
                'Filename':outfile.rstrip('.txt'),       # File name
                'Time Taken': str(time_taken),                # Time taken
                'document_type': word_lc,                   # Equivalent LC word
                'scanned_text': text
                }

    return retJSON


def extract(outfile, word_lc, start_time):
    
    #%% Part #3 - Initialisation
            
    FoDC_F40a = 'NA'                    # F40 : Form of documentary credit
    AoDC_F50 = 'NA'                     # F50 : Applicant of the documentary credit
    BoDC_F59 = 'NA'                     # F59 : Beneficiary of the documentary credit
    ARoDC_F40E = 'NA'                   # F40E : Applicable rules of the documentary credit
    DoDC_F31C = 'NA'                    # F31C : Date of issue of the documentary credit
    Dexp_oDC_F31D = 'NA'                # 31D : Date and place of expiry of the documentary credit
    # Pexp_oDC_F31D,                    # 31D : Date and place of expiry of the documentary credit           
    Cur_oDC_F32B = 'NA'                 # 32B : Currency code and amount of the documentary credit
    # 'Amt_oDC_F32B': Amt_oDC_F32B,     # 32B : Currency code and amount of the documentary credit
    PCAT1_F39A = 'NA'                   # 39A : Percentage Credit Amount Tolerance
    # 'PCAT2_F39A': PCAT2_F39A,         # 39A : Percentage Credit Amount Tolerance
    Maxca_F39B = 'NA'                   # 39B : Maximum Credit Amount
    PT1_oDC_F41A = 'NA'                 # 41A : Payment terms of the documentary credit
    # 'PT2_oDC_F41A': PT2_oDC_F41A,     # 41A : Payment terms of the documentary credit
    PS_F43P = 'NA'                      # 43P : Partial shipments
    PTrans_F43T = 'NA'                  # 43T : Transhipment
    PLoad_F44E = 'NA'                   # 44E : Port of Loading
    PDis_F44F = 'NA'                    # 44F : Port of Discharge
    DS_44C = 'NA'                       # 44C : Latest date of shipment of the documentary credit
    Des_goods_F45A = 'NA'               # 45A : Description of Goods &/or Services
    Dr_46A = 'NA'                       # 46A : Documents Required
    Ac_47A = 'NA'                       # 47A : Additional Conditions
    Ch_71B = 'NA'                       # 71B : Charges
    Pp1_48 = 'NA'                       # 48 : Period for Presentation
    #'Pp2_48': Pp2_48,                  # 48 : Period for Presentation
    CI_49 = 'NA'                        # 49 : Confirmation Instructions
    Rb_53a = 'NA'                       # 53A : Reimbursing Bank – BIC
    Ipab_78 = 'NA'                      # 78 : Instructions to Paying/Accepting/Negotiating Bank
    ATB_57D = 'NA'                      # 57D : `Advise Through` Bank -Name & Address
    
    #%% Part #4 - Extract Information from text file
    with open(outfile) as f:
        # content = f.readlines()
        lines = [line.rstrip('\n') for line in f]
    # you may also want to remove whitespace characters like `\n` at the end of each line
    
    for i in range(0,len(lines)):
        # print(i)
        
        # F40 : Form of documentary credit
        if '40A:' in lines[i]:
            j = i;
            while '20:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                FoDC_F40a = "\n".join(lines[i+1:j]).strip()
            
        # F50 : Applicant of the documentary credit
        elif '50:' in lines[i]:
            j = i;
            while '59:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                AoDC_F50 = "\n".join(lines[i+1:j]).strip()
    
        # F59 : Beneficiary of the documentary credit
        elif '59:' in lines[i]:
            j = i;
            while '32B:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                BoDC_F59  = "\n".join(lines[i+1:j]).strip()
           
        # F40E : Applicable rules of the documentary credit
        elif '40E:' in lines[i] or 'AOE:' in lines[i]:
            j = i;
            while '31D:' not in lines[j] and '34D' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                ARoDC_F40E = "\n".join(lines[i+1:j]).strip()
    
        # F31C : Date of issue of the documentary credit
        elif '31C:' in lines[i]:
            j = i;
            while 'AOE' not in lines[j] and '40E' not in lines[j] and '4OE:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                DoDC_F31C = "\n".join(lines[i+1:j]).strip()
            
        # 31D : Date and place of expiry of the documentary credit
        elif '31D:' in lines[i]:
            j = i;
            while '50:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Dexp_oDC_F31D = "\n".join(lines[i+1:j]).strip()
    
        # 32B : Currency code and amount of the documentary credit
        elif '32B:' in lines[i]:
            j = i;
            while '39B' not in lines[j] and '39A' not in lines[j]:
            # while ('39B' or '39A') not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Cur_oDC_F32B = "\n".join(lines[i+1:j]).strip()
    
        # 39A : Percentage Credit Amount Tolerance
        elif '39A:' in lines[i]:
            j = i;
            while '41D' not in lines[j] and '41A' not in lines[j] and 'A1A' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                PCAT1_F39A = "\n".join(lines[i+1:j]).strip()
                        
        # 39B : Maximum Credit Amount
        elif '39B:' in lines[i]:
            j = i;
            while '41A:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Maxca_F39B = "\n".join(lines[i+1:j]).strip()
    
        # 41A : Payment terms of the documentary credit
        elif '41A:' in lines[i] or 'A1A:' in lines[i]:
            j = i;
            while '43P' not in lines[j] and '42P' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                PT1_oDC_F41A = "\n".join(lines[i+1:j]).strip()
    
        # 43P : Partial shipments
        elif '43P:' in lines[i]:
            j = i;
            while '43T:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                PS_F43P = "\n".join(lines[i+1:j]).strip()
    
        # 43T : Transhipment
        elif '43T:' in lines[i]:
            j = i;
            while '44E:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                PTrans_F43T = "\n".join(lines[i+1:j]).strip()
            
        # 44E : Port of Loading
        elif '44E:' in lines[i]:
            j = i;
            while '44F:' not in lines[j] and 'A4F' not in lines[j]:
                j= j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                PLoad_F44E = "\n".join(lines[i+1:j]).strip()
            
        # 44F : Port of Discharge
        elif '44F:' in lines[i] or 'A4F:' in lines[i]:
            j = i;
            while '44C:' not in lines[j]:
                j= j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                PDis_F44F = "\n".join(lines[i+1:j]).strip()
            
        # 44C : Latest date of shipment of the documentary credit
        elif '44C:' in lines[i]:
            j = i;
            while '45A:' not in lines[j]:
                # print(lines[j])
                j= j+1
                # print(j)
            if "\n".join(lines[i+1:j]).strip() != "":
                DS_44C = "\n".join(lines[i+1:j]).strip()
    
        # 45A : Description of Goods &/or Services
        elif '45A:' in lines[i]:
            j = i;
            while '46A:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Des_goods_F45A = "\n".join(lines[i+1:j]).strip()
    
        # 46A : Documents Required
        elif '46A:' in lines[i]:
            # print(i)
            j = i;
            while '47A:' not in lines[j] and '474A:' not in lines[j]:
                # print(lines[j])
                j= j+1
                # print(j)
            if "\n".join(lines[i+1:j]).strip() != "":
                Dr_46A = "\n".join(lines[i+1:j]).strip()
            
        # 47A : Additional Conditions
        elif '47A:' in lines[i] or '474A:' in lines[i]:
            j = i;
            while '71B' not in lines[j] and '71D' not in lines[j]:
            # while '71B:' not in lines[j]:
                # print(lines[j])
                j= j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Ac_47A = "\n".join(lines[i+1:j]).strip()
    
        # 71B : Charges
        elif '71B:' in lines[i]:
            j = i;
            while '48:' not in lines[j] and 'A8:' not in lines[j]:
                # print(lines[j])
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Ch_71B = "\n".join(lines[i+1:j]).strip()
            
        # 48 : Period for Presentation
        elif '48:' in lines[i] or 'A8:' in lines[i]:
            j = i;
            while '49:' not in lines[j]:
                # print(lines[j])
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Pp1_48 = "\n".join(lines[i+1:j]).strip()
    
        # 49 : Confirmation Instructions
        elif '49:' in lines[i]:
            j = i;
            while '53A' not in lines[j] and '78' not in lines[j]:
            # while '53A:' not in lines[j]:
                # print(lines[j])
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                CI_49 = "\n".join(lines[i+1:j]).strip()
            
        # 53A : Reimbursing Bank – BIC
        elif '53A:' in lines[i]:
            j = i;
            while '78:' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Rb_53a = "\n".join(lines[i+1:j]).strip()
    
        # 78 : Instructions to Paying/Accepting/Negotiating Bank
        elif '78:' in lines[i]:
            j = i;
            while '57D' not in lines[j] and '57A' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                Ipab_78 = "\n".join(lines[i+1:j]).strip()
            
        # 57D : `Advise Through` Bank - Name & Address
        elif '72:' in lines[i] or '57D:' in lines[i]:
            j = i;
            while 'I agree' not in lines[j] and 'MAC:' not in lines[j] and 'Network Data' not in lines[j]:
                j = j+1
            if "\n".join(lines[i+1:j]).strip() != "":
                ATB_57D = "\n".join(lines[i+1:j]).strip()
#%% Timer ends
    time_taken = round(time.time() - start_time,2)

#%% Part $5 - Compiling extracted data into a dataframe
    retJSON = { 
                'Filename':outfile.rstrip('.txt'),       # File name
                'Time Taken': str(time_taken),                # Time taken
                'document_type': word_lc,                   # Equivalent LC word
                'FoDC_F40a':FoDC_F40a,                   # F40 : Form of documentary credit
                'AoDC_F50':AoDC_F50,                     # F50 : Applicant of the documentary credit
                'BoDC_F59':BoDC_F59,                     # F59 : Beneficiary of the documentary credit
                'ARoDC_F40E':ARoDC_F40E,                 # F40E : Applicable rules of the documentary credit
                'DoDC_F31C':DoDC_F31C,                   # F31C : Date of issue of the documentary credit
                'Dexp_oDC_F31D':Dexp_oDC_F31D,           # 31D : Date and place of expiry of the documentary credit
                'Cur_oDC_F32B': Cur_oDC_F32B,            # 32B : Currency code and amount of the documentary credit
                'PCAT1_F39A': PCAT1_F39A,                # 39A : Percentage Credit Amount Tolerance
                'Maxca_F39B': Maxca_F39B,                # 39B : Maximum Credit Amount
                'PT1_oDC_F41A': PT1_oDC_F41A,            # 41A : Payment terms of the documentary credit
                'PS_F43P': PS_F43P,                      # 43P : Partial shipments
                'PTrans_F43T': PTrans_F43T,              # 43T : Transhipment
                'PLoad_F44E': PLoad_F44E,                # 44E : Port of Loading
                'PDis_F44F': PDis_F44F,                  # 44F : Port of Discharge
                'DS_44C': DS_44C,                        # 44C : Latest date of shipment of the documentary credit
                'Des_goods_F45A': Des_goods_F45A,        # 45A : Description of Goods &/or Services
                'Dr_46A': Dr_46A,                        # 46A : Documents Required
                'Ac_47A': Ac_47A,                        # 47A : Additional Conditions
                'Ch_71B': Ch_71B,                        # 71B : Charges
                'Pp1_48': Pp1_48,                        # 48 : Period for Presentation
                'CI_49': CI_49,                          # 49 : Confirmation Instructions
                'Rb_53a': Rb_53a,                        # 53A : Reimbursing Bank – BIC
                'Ipab_78': Ipab_78,                      # 78 : Instructions to Paying/Accepting/Negotiating Bank
                'ATB_57D': ATB_57D                       # 57D : `Advise Through` Bank -Name & Address
                }
    
    return retJSON
