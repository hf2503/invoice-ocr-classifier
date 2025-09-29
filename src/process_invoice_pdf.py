import pytesseract
import numpy as np
from datetime import datetime
import cv2
import os
from PIL import Image
import logging
import csv

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

#creation Train_dir 
os.makedirs(config.TRAIN_DIR,exist_ok = True)

#dictionnary_list:
row_list = []




def process_invoice_pdf(input_pdf:str,
                        train_dir=config.TRAIN_DIR,
                        train_final= config.TRAIN_FINAL,
                        company_csv = config.company_df,
                        list_company_invoice=config.LIST_COMPANY_NAME_INVOICE,
                        list_company_tva = config.LIST_COMPANY_TVA,
                        output_dir= config.OUTPUT_DIR,
                        list_supplier= config.LIST_SUPPLIER,
                        list_tva_supplier= config.LIST_TVA_SUPPLIER,
                        new_supplier= config.NEW_SUPPLIER,
                        new_company= config.NEW_COMPANY
                        ):
    """
    convert the Image PIL into pdf files

    Args:
        image : invoice image 
    """
    if not os.path.exists(input_pdf):
        logging.error("file %s not found",input_pdf)
        raise FileNotFoundError(f"the file {input_pdf} is not found")

   
    #convert pdf into image
    images = convert_pdf_to_PIL(input_pdf)
    
    for i,image in enumerate(images):
        
        #convert image PIL in RGB 
        image_rgb = image.convert("RGB")
        
        
        #preprocessing for pytesseract
        img_array = np.array(image_rgb)
        #filtered_image = cv2.bilateralFilter(img_array, 9, 75, 75)
        gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        #adaptive_threshold = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 10)
        
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
            #image_filename = f"{os.path.basename(input_pdf)[0:8]}_{i+1}.png"
            image_filename = f"{os.path.basename(input_pdf)}_{i+1}.png"
            train_image_path = os.path.join(train_dir,image_filename)
            train_image_path_final = os.path.join(train_final,image_filename)
            image.save(train_image_path)
            image.save(train_image_path_final)
            logging.info("l'image est enregistré dans : %s",train_image_path)


            #----------feature train_image_path------------
            row['train_image_path'] = image_filename

            directory_company_path = None
            directory_parent_company = None
            clean_text_ocr = clean_text(text)


            #----- COMPANY DETECTION--------
            company_name = check_company(clean_text_ocr,
                                         company_df=company_csv,
                                         company_list_name_invoice=list_company_invoice,
                                         company_list_tva=list_company_tva,
                                         new_company=new_company
                                         )
            

            logging.debug("Detected company name : %s", company_name)

            print(f"company name : {company_name}")


            if isinstance(company_name, tuple) :

                #directory_parent_match = company_csv.loc[company_csv['parent_company'] == company_name[0],'parent_company'].values
                directory_parent_match = company_csv.loc[company_csv['company_name_invoice'] == company_name[1],'parent_company'].values
                directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name[1],'company_name_registery'].values
                
                
                logging.info("directory_company_match_size: %s",directory_company_match.size)
                
                
                                    
                #-------------deboguage----------------
                    
                    
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

                    logging.info("ddirectory_company:%s:",directory_company)

                    directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)

                    logging.info("directory_company_path:%s:",directory_company_path)

                    logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                    print(directory_company_path)
                
                else:
                    #-------------deboguage----------------
                    logging.info("directory_parent_match_debogage_2: %s",directory_parent_match)
                    logging.info("directory_company_match_debogage_2: %s",directory_company_match)
                    
                    
                    #-------------fin_debogage------------------
                    
                    logging.info("company_name[1] : %s",company_name[1])
                    logging.info("company_name[0] : %s",company_name[0])
                    logging.info("company name '%s' not found in registry; fallback to '%s'",company_name[0],company_name[1])



                    #-------------deboguage----------------
                    
                    logging.info("row_debogage_3: %s",row)
                    
                    
                    #-------------fin_debogage------------------


                    #------------feature parent_company-----------

                    row['parent_company'] = directory_parent_match[0]

                    #------feature company_name-------

                    row['company_name'] = directory_company_match[0]
                    
                    
                    directory_parent_company = directory_parent_match[0]
                    directory_company = directory_company_match[0]
                    
                    
                    # directory_parent_company = company_name[0]
                    # directory_company = company_name[1]
                    
                    
                    #-------------deboguage----------------
                    
                    logging.info("directory_parent_company_debogage_4: %s",directory_parent_company)
                    logging.info(" directory_company_debogage_4: %s",directory_company)
                    
                    #-------------fin_debogage------------------
                    
                    
                    
                    directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)


            elif company_name in list_company_invoice or company_name == 'new_company':
                directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values

                #------------feature parent_company-----------
                
                #-------------MODIF 19/09/2025-----------
                
                #row['parent_company'] = company_name
                #--------------FIN MODIF ------------------------

                if directory_company_match.size > 0:
                    
                    #-----------MODIF 19/09/2025--------------
                    print(f"directory_company_match{directory_company_match}")
                    row['parent_company'] = directory_company_match[0]
                    
                    #--------------FIN MODIF ------------------------
                    
                    print(f"directory_company_match{directory_company_match}")
                    directory_company = directory_company_match[0]   
                    directory_company_path = make_directory_company(output_dir,directory_company)
                    logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                    print(directory_company_path)
                else:
                    #------------MODIF 19/09/2025-------------
                    row['parent_company'] = new_company
                    
                    #--------------FIN MODIF ------------------------
                    
                    logging.info("company name '%s' not found in registry; fallback to '%s'",company_name,new_company)
                    directory_company_path = make_directory_company(output_dir,new_company)

            else:
                logging.warning("company name '%s' not matched anywhere; fallback to '%s'", company_name, new_company)
                directory_company_path = make_directory_company(output_dir, new_company)



            #supplier detection
            supplier_name = check_supplier(clean_text_ocr,supplier_list=list_supplier,tva_supplier_list=list_tva_supplier)
            

            if supplier_name:
                norm_name = normalise_supply_name(text = supplier_name)

            else:
                norm_name = normalise_supply_name(text =new_supplier)
            
            dir_path_supply = make_directory_supply(directory_company=directory_company_path,directory_supplier=norm_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            invoice_path = os.path.join(dir_path_supply,f"facture{timestamp}.pdf")
            
            #----------convert_pdf_format------------
            resized_image = image.resize((2000, 2000),Image.Resampling.LANCZOS)
            resized_image.convert('RGB').save(invoice_path)
            logging.info("invoice save to : %s",invoice_path)

            #--------feature supplier_name-------------
            row['supplier_name'] = norm_name

            row_list.append(row)
     
        else:
            logging.info("invoice's page rejected ")
    
    #-------------sauvegarde du dataframe----------------
    
    # logging.info("row_list %s", row_list)
    # timestamp_2 = datetime.now().strftime("%Y%m%d_%H%M%S")
    train_data = pd.DataFrame(row_list)
    train_data_final = pd.DataFrame(row_list)
    train_data_path = os.path.join(train_dir,'train_data.csv')
    train_final_path = os.path.join(train_final,'train_final.csv')
    
    if os.path.exists(train_data_path):
        logging.info("train_data.csv found, appending new_data....")
        existing_data= pd.read_csv(train_data_path,encoding='utf_8')
        train_data = pd.concat([existing_data,train_data],ignore_index=True)
        train_data_final = pd.concat([existing_data,train_data],ignore_index=True)
    else:
        logging.info("the file train_data.csv not found, creating a new file ")
        
    
    logging.info(f"train_data.csv updated : n_rows = {train_data.shape[0]} n_columns ={train_data.shape[1]}")
    
    train_data.to_csv(train_data_path,index=False,encoding='utf-8')
    train_data_final.to_csv(train_final_path,index=False,encoding='utf-8')