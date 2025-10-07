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


print(f"Tesseract path loaded: {config.TESSERACT_PATH}")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)

#desactivate the debug message of pillow in the file invoice_processing.log
logging.getLogger('PIL').setLevel(logging.WARNING)


#Pytesseract_path
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

#dictionnary_list:
row_list = []

def suivi_csv(file_path,csv_path = config.SUIVI_CSV,row=None,columns=config.COLUMNS_SUIVI):

    #création du dossier suivi
    os.makedirs(os.path.dirname(csv_path),exist_ok=True)

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    sha1_pdf = extract_SHA1(file_path)

    #valeur pour ecriture
    values = list(row.values()) + [date,sha1_pdf]
    
    #on test si le csv existe
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path,'a',newline='',encoding='utf-8') as f:
        writer = csv.writer(f,delimiter=';')
        if not file_exists:
            writer.writerow(columns)
        writer.writerow(values)


def process_invoice_pdf(input_pdf:str,
                        suivi_dir=config.SUIVI_DIR,
                        archive_suivi_dir=config.FACTURE_CLASSEES_DIR, 
                        company_csv = config.company_df,
                        list_company_invoice=config.LIST_COMPANY_NAME_INVOICE,
                        output_dir= config.OUTPUT_DIR,
                        list_supplier= config.LIST_SUPPLIER,
                        new_supplier= config.NEW_SUPPLIER,
                        new_company= config.NEW_COMPANY
                        ):
    """
    convert the Image PIL into pdf files

    Args:
        image : invoice image 
    """
    
    #création des dossiers
    
    os.makedirs(suivi_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_suivi_dir,exist_ok=True)
    
    if not os.path.exists(input_pdf):
        logging.error("file %s not found",input_pdf)
        raise FileNotFoundError(f"the file {input_pdf} is not found")

    #dictionnary_list:
    row_list = []
    
    #convert pdf into image
    images = convert_pdf_to_PIL(input_pdf)
    
    for i,image in enumerate(images):
        
        #convert image PIL in RGB 
        image_rgb = image.convert("RGB")
        
        
        #preprocessing for pytesseract
        img_array = np.array(image_rgb)
        
        
        gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        
        #convert image to string
        try:
            text = pytesseract.image_to_string(gray_image,config="--psm 6")
                
        except Exception as e:
            
            logging.error("L'OCR pytesseract failed on page %d of file %s: %s", i+1,os.path.basename(input_pdf),e)
            continue
        
        
        if check_invoice(text):

            #feature_dictionnary
            row={}
            
            #-----------SAVED IMAGE------------
            
            image_filename = f"{os.path.basename(input_pdf)}_{i+1}.png"
            archive_image_path = os.path.join(suivi_dir,archive_suivi_dir,image_filename)
            image.save(archive_image_path)
            logging.info("l'image est enregistré dans : %s",archive_image_path)


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
                
                
                
                
                logging.info("directory_company_match_size: %s",directory_company_match.size)
                
                
                                    
                #-------------debogage----------------
                    
                    
                logging.info("directory_parent_match_debogage_1: %s",directory_parent_match)
                logging.info("directory_company_match_debogage_1: %s",directory_company_match)
                    
                    
                #-------------fin_debogage------------------
            
                
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

                    logging.info("directory_company_path:%s:",directory_company_path)

                    logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                    print(directory_company_path)
                
                else:
                    #-------------debogage----------------
                    logging.info("directory_parent_match_debogage_2: %s",directory_parent_match)
                    logging.info("directory_company_match_debogage_2: %s",directory_company_match)
                    
                    
                    #-------------fin_debogage------------------
                    
                    logging.info("company_name[1] : %s",company_name[1])
                    logging.info("company_name[0] : %s",company_name[0])
                    logging.info("company name '%s' not found in registry; fallback to '%s'",company_name[0],company_name[1])



                    #-------------debogage----------------
                    
                    logging.info("row_debogage_3: %s",row)
                    
                    
                    #-------------fin_debogage------------------


                    #------------feature parent_company-----------

                    row['parent_company'] = directory_parent_match[0]

                    #------feature company_name-------

                    row['company_name'] = directory_company_match[0]
                    
                    
                    directory_parent_company = directory_parent_match[0]
                    directory_company = directory_company_match[0]
                    
                    
                    #-------------debogage----------------
                    
                    logging.info("directory_parent_company_debogage_4: %s",directory_parent_company)
                    logging.info(" directory_company_debogage_4: %s",directory_company)
                    
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



            #--------------supplier detection----------------------
            supplier_name = check_supplier(clean_text_ocr,supplier_list=list_supplier)
            

            if supplier_name:
                norm_name = normalise_supply_name(text = supplier_name)

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

            suivi_csv(invoice_path,csv_path = config.SUIVI_CSV,row=row)
     
        else:
            logging.info("invoice's page rejected ")
    
    
        #-------------Fin sauvegarde de la row_list dans le fichier suivi.csv----------------
    
