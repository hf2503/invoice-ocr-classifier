"""
    invoice processing and filing utilities

    this module : 
      - configure Tesseract path and logging
      - converts PDFs to images and performs OCR with pytesseract
      - detects the target company, parent company and the supplier
      - create the folder structure and save the invoice's page in pdf/png format according to the filing logic
      - save the results into CSV files

"""

import pytesseract
import numpy as np
import pandas as pd
from datetime import datetime
import cv2
import os
from PIL import Image
import logging
import csv
import datetime


from . import config
from .utils import *


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)

logging.info(f"Tesseract path loaded: {config.TESSERACT_PATH}")

#desactivate the debug message of pillow in the file invoice_processing.log
logging.getLogger('PIL').setLevel(logging.WARNING)


#Pytesseract_path
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

#dictionnary_list:
row_list = []

def suivi_resultat_csv(file_path:str,
                       csv_path_suivi = config.SUIVI_CSV,
                       csv_path_result = config.RESULTAT_CSV,
                       row=None,
                       columns=config.COLUMNS_SUIVI):
    """
    Append one result row to the CSV files 

    this function : 

    - compute the current date, the SHA-1 hash of the file and append them to the row 
    - append the row to csv_path_suivi and csv_path_result

    Args:
        file_path (str): path to the actual saved invoice file
        csv_path_suivi (str): path to the tracking csv file that archives the results
        csv_path_result (str): path to the csv file containing the result of the processing 
        row (dict): the dict who contains the reults of the processing
        columns (list[str]): CSV header to write if the file does not exist

    returns

        None: Write to the disk, no values is returned
    
    """

    #création du dossier suivi
    os.makedirs(os.path.dirname(csv_path_suivi),exist_ok=True)

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    sha1_pdf = extract_SHA1(file_path)
    
    #valeur pour ecriture dans le fichier suivi.csv
    values = list(row.values()) + [date,sha1_pdf]
    
    #on test si  suivi.csv et resultat.csv existe
    file_exists_suivi = os.path.exists(csv_path_suivi)
    file_exists_result = os.path.exists(csv_path_result)
    
    #ajout des resultats dans le fichier suivi.csv
    with open(csv_path_suivi,'a',newline='',encoding='utf-8') as f:
        writer = csv.writer(f,delimiter=';')
        if not file_exists_suivi:
            writer.writerow(columns)
        writer.writerow(values)
    
    #ecriture des resultats dans resultats.csv  
    with open(csv_path_result,'a',newline='',encoding='utf-8') as f:
        writer = csv.writer(f,delimiter=';')
        if not file_exists_result:
            writer.writerow(columns)
        writer.writerow(values)



def process_invoice_pdf(input_pdf:str,
                        key_word = config.VALIDATION_KEYWORD,
                        suivi_dir=config.SUIVI_DIR,
                        archive_suivi_dir=config.FACTURE_CLASSEES_DIR, 
                        company_csv = config.company_df,
                        supplier_csv = config.supplier_df,
                        list_company_invoice=config.LIST_COMPANY_NAME_INVOICE,
                        output_dir= config.OUTPUT_DIR,
                        list_supplier= config.LIST_SUPPLIER,
                        list_tva_supplier = config.LIST_TVA_SUPPLIER,
                        new_supplier= config.NEW_SUPPLIER,
                        new_company= config.NEW_COMPANY
                        ):
    """

    process a pdf file containing numerous invoices

    the function perfomr the following tasks:
        - convert the pdf file into PIL format
        - convert each image into string format
        - filter the image 


    Args:
        input_pdf (str): Path to the actual pdf file containing numerous invoices
        suivi_dir (str): Folder tracking for processed invoice. Defaults to config.SUIVI_DIR.
        archive_suivi_dir (str): Folder containing the process invoice filed into their corresponding folder . Defaults to config.FACTURE_CLASSEES_DIR.
        company_csv (pandas.DataFrame): DataFrame containing the name of companies, parent companies and TVA. Defaults to config.company_df.
        list_company_invoice (list[str]): list containing the name of the company . Defaults to config.LIST_COMPANY_NAME_INVOICE.
        output_dir (str): Path of the folder who contains the filed invoices. Defaults to config.OUTPUT_DIR.
        list_supplier (list[str]): Fallback label. Defaults to config.LIST_SUPPLIER.
        new_supplier (str): Fallback label when no supplier has been identified . Defaults to config.NEW_SUPPLIER.
        new_company (_type_, optional): Fallback label when no company has been identified . Defaults to config.NEW_COMPANY.

    Return:

        None : Writes files to disk, logs, and updates tracking csv    
    
        
    Side Effects :
        - create directories
        - Writes/appends lines to csv files
        - produces log messages
    
    Raises:
        FileNotFoundError: _description_
        Exception : any exception from ocr

    
    
    """
    
    #création des dossiers
    
    os.makedirs(suivi_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_suivi_dir,exist_ok=True)
    
    if not os.path.exists(input_pdf):
        logging.error("file %s not found",input_pdf)
        raise FileNotFoundError(f"the file {input_pdf} is not found")
    
    
    # invoice page
    page = {}
    page_no_key = {}
    page_with_key = {}

    #dictionnary_list:
    row_list = []
    
    #convert pdf into image
    images = convert_pdf_to_PIL(input_pdf)
    
    for i,image in enumerate(images):
        
        #-----------SAVED IMAGE------------
        
        # conversion of pdf format into PNG format
        image_filename = f"{os.path.basename(input_pdf)}_{i+1}.png"
        
        #save the image
        archive_image_path = os.path.join(suivi_dir,archive_suivi_dir,image_filename)
        image.save(archive_image_path)
        logging.info("l'image est enregistré dans : %s",archive_image_path)
        
        # #convert image PIL in RGB 
        # image_rgb = image.convert("RGB")
        
        # #preprocessing for pytesseract
        # img_array = np.array(image_rgb)
        # gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        #---------------------------test avec des image au format PNG-----------------------------
        
        #open the image PNG of the invoice
        # img = Image.open(archive_image_path)
        
        img = cv2.imread(archive_image_path)
        
        #preprocessing for pytesseract
        # img_RGB = img.convert('RGB')
        # img_array = np.array(img_RGB)
        # img_grey = cv2.cvtColor(img_array,cv2.COLOR_BGR2GRAY)
        
        img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        threshold_img = cv2.threshold(img_gray , 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
         #---------------------------test concluant pytesseract fonctionne mieux avec des fichier au format PNG-----------------------------
        
        #convert image to string
        try:
            text = pytesseract.image_to_string(threshold_img  ,config="--psm 6")
            
            # text = pytesseract.image_to_string(gray_image,config="--psm 6")
            # logging.info(f"text_pytesseract : {text}")

                
        except Exception as e:
            
            logging.error("L'OCR pytesseract failed on page %d of file %s: %s", i+1,os.path.basename(input_pdf),e)
            continue
    
    # -------------------------- Detection de facture multipage--------------------------

        
        
        
        
        text_ocr = clean_text(text)
        
        logger.info(text)
        
        
        
        
        # caracterisitics of invoice's page
        
        page["company"] = check_company(text=text_ocr,
                                        company_df=company_csv,
                                        new_company=new_company)
        
        page["supplier"] = check_supplier(ocr_text=text_ocr,
                                          supplier_list=list_supplier)
        
        page["key_word"] = check_invoice(text=text_ocr,
                                         key_word=key_word)
        
        page['tva'] = check_tva_supplier(ocr_text=text_ocr,
                                         list_supplier=list_supplier,
                                         list_tva=list_tva_supplier)
        
        page['path'] = archive_image_path
        
        
        logger.info(f"page : {page}") 
        
        
        if not page["key_word"]:
            page_no_key = page.copy()
            continue
        
        page_with_key = page.copy()
            
           
        #case where invoice has its pages in order
        
        if page_no_key and page_with_key: 
            if page_no_key["company"] != new_company and page_with_key['company'] == new_company and (page_no_key['supplier'] == page_with_key['supplier'] or 
                                                                                                      page_no_key['tva'] == page_with_key['tva']):
                img_concat = cv2.vconcat([cv2.imread(page_no_key['path']),cv2.imread(page_with_key['path'])])
                try:
                    text = pytesseract.image_to_string(img_concat,config="--psm 6")
                    text_ocr = clean_text(text)
                    
                    #reset of the variable page, page_no_key,page_with_key
                    page_no_key = {}
                    page_with_key = {}
                except Exception as e:
                    logging.error(f"on a eu l'erreur suivant pour la multiple facture {page['path']} : {e} ")                   
         
       
        if check_invoice(text=text_ocr,key_word=key_word):

            #feature_dictionnary
            row={}
            
            #----------feature train_image_path------------
            
            row['train_image_path'] = image_filename

            directory_company_path = None
            directory_parent_company = None
            clean_text_ocr = clean_text(text)

            #----- COMPANY DETECTION--------
            company_name = check_company(clean_text_ocr,
                                         company_df=company_csv,
                                         new_company=new_company
                                         )
            
            logging.debug("Detected company name : %s", company_name)

            print(f"company name : {company_name}")

            if isinstance(company_name, tuple) :

                #directory_parent_match = company_csv.loc[company_csv['parent_company'] == company_name[0],'parent_company'].values
                directory_parent_match = company_csv.loc[company_csv['company_name_invoice'] == company_name[1],'parent_company'].values
                directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name[1],'company_name_registery'].values
                                
                logging.info("directory_company_match_size LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s",directory_company_match.size)    
                logging.info("directory_parent_match_debogage_1 LBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB: %s",directory_parent_match)
                logging.info("directory_company_match_debogage_1 LCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC: %s",directory_company_match)
                     
                if directory_company_match.size > 1 :
                    
                    directory_parent_company = directory_parent_match[0]

                    #------------feature parent_company-----------

                    row['parent_company'] = directory_parent_match[0]

                    #------feature company_name-------
                    row['company_name'] = directory_parent_match[1]

                    logging.info("directory_parent_company:%s:",directory_parent_company)

                    directory_company = directory_company_match[0]  

                    logging.info("directory_company:%s:",directory_company)

                    directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)

                    # logging.info("directory_company_path:%s:",directory_company_path)

                    # logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                
                else:

                    #------------feature parent_company-----------

                    row['parent_company'] = directory_parent_match[0]
                    
                    logging.info("parent_company LDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD: %s",row['parent_company']) 

                    #------feature company_name-------

                    row['company_name'] = directory_company_match[0]
                    
                    logging.info("'company_name' LEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE: %s",row['company_name']) 
                    
                    directory_parent_company = directory_parent_match[0]
                    directory_company = directory_company_match[0]
                    
                    #-------------debogage----------------
                    
                    # logging.info("directory_parent_company_debogage_4: %s",directory_parent_company)
                    # logging.info(" directory_company_debogage_4: %s",directory_company)
                    
                    #-------------fin_debogage------------------
                    
                    directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)

            #------------------cas ou il n'y a pas de societe mere------------------
            elif company_name in list_company_invoice or company_name == 'new_company':
                directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values
                
                #------------------pas de société mère--------------
                row['parent_company'] = 0

                
                if directory_company_match.size > 0:
                    
   
                    logging.info(f"directory_company_match : {directory_company_match}")
                    
                    row['company_name'] = directory_company_match[0]
                    
                    # row['parent_company'] = directory_company_match[0]
                    
                    
                    
                    directory_company = directory_company_match[0]   
                    directory_company_path = make_directory_company(output_dir,directory_company)
                    logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                    print(directory_company_path)
                else:
                    row['company_name'] = new_company
                    #row['parent_company'] = new_company
                    logging.info("company name '%s' not found in registry; fallback to '%s'",company_name,new_company)
                    directory_company_path = make_directory_company(output_dir,new_company)

            else:
                logging.warning("company name '%s' not matched anywhere; fallback to '%s'", company_name, new_company)
                directory_company_path = make_directory_company(output_dir, new_company)

            # logging.info(f"list_supplier : {list_supplier}")

            #--------------supplier detection----------------------
            supplier_name = check_supplier(clean_text_ocr,
                                           supplier_list=list_supplier)
            
            # logging.info(f'ocr_text : {clean_text_ocr}')
            # 
            # logging.info(f'raw_text : {text.lower()}')
            


            if supplier_name:
                
                registery_name = supplier_csv[supplier_csv['supplier_invoice'] == supplier_name]['supplier_registery'].unique()
                norm_name = normalise_supply_name(text = registery_name[0])

            else:
            #on retente le process sur l'image png sauvegardé , le deuxième traitement arrive souvent à identifier le supplier    
                image_retry = Image.open(archive_image_path)

            # #on met l'image au standard RGB
                image_retry_rgb = image_retry.convert("RGB")

            # #on convertit l'image en tableau numpy
                image_retry_array = np.array(image_retry_rgb)

            # # conversion de l'image en niveau de gris
                image_retry_gray = cv2.cvtColor(image_retry_array,cv2.COLOR_BGR2GRAY)
            
            #on detecte le texte de l'image grace à pytesseract
                text_retry = pytesseract.image_to_string(image_retry_gray)
                clean_text_retry_ocr = clean_text(text_retry) 

            #--------------------debogage------------------------
                logging.info(f"text_retry_ocr = {clean_text_retry_ocr}")
            #---------------------fin debogage-------------------

            #on retry la fonction check supply sur la facure qui a été enregistré au format png
                supplier_name_retry = check_supplier(ocr_text =clean_text_retry_ocr,
                                                     supplier_list = list_supplier) 
              
                if supplier_name_retry:
                    registery_name = supplier_csv[supplier_csv['supplier_invoice'] == supplier_name_retry]['supplier_registery'].unique()
                    norm_name = normalise_supply_name(text = registery_name[0])
                else:
                    norm_name = normalise_supply_name(text =new_supplier)
        
            #--------------creation du chemin de la facture-----------------------    
            
            dir_path_supply = make_directory_supply(directory_company=directory_company_path,directory_supplier=norm_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            invoice_path = os.path.join(dir_path_supply,f"facture{timestamp}.pdf")
            
            #----------convert_pdf_format + sauvegarde ------------
            
            resized_image = image.resize((2000, 2000),Image.Resampling.LANCZOS)
            resized_image.convert('RGB').save(invoice_path)
            logging.info("invoice save to : %s",invoice_path)

            #--------feature supplier_name-------------
            row['supplier_name'] = norm_name

            row_list.append(row)

            #-------------sauvegarde de la row dans le fichier suivi.csv----------------

            suivi_resultat_csv(file_path=invoice_path,row=row)
            
            
            
     
        else:
            logging.info("invoice's page rejected ")
    
    
        #-------------Fin sauvegarde de la row_list dans le fichier suivi.csv----------------
    
