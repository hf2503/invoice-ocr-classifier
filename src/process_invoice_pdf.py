"""
    invoice processing and filing utilities

    this module provide an end-to-end pipeline to extract, validate, 
    and file scanned invocies from pdf documents . It combines PDF-to-image conversion,
    OpenCV preprocessing, OCR extraction using pytesseract and ruke-based matching to detect companies, 
    parent companies, suppliers, and supplier VAT numbers.
    Classified invoices are then saved to a structured output directory and tracked
    in CSV files.

    The differents actions of this module are : 
    
    - Configure Tesseract (path) and application logging
    - Convert input PDFs into page images and run OCR (pytesseract)
    - Analyze each page to detect:
        * target company / parent company
        * supplier name and/or supplier VAT number
        * invoice validation keyword
    - Detect two-page invoices and optionally concatenate page images
    - Create the output folder structure and save each classified invoice as PDF
    - Append processing results to tracking CSV files

"""

import pytesseract
import numpy as np
import pandas as pd
from datetime import datetime
import cv2
import os
import io
from PIL import Image
from PIL import ImageFile
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
    with open(csv_path_suivi,'a',newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f,delimiter=';')
        if not file_exists_suivi:
            f.write("sep=;\n")
            writer.writerow(columns)
        writer.writerow(values)
    
    #ecriture des resultats dans resultats.csv  
    with open(csv_path_result,'a',newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f,delimiter=';')
        if not file_exists_result:
            f.write("sep=;\n")
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
    
    This function processes an input PDF containing scanned invoices and automatically classifies
    the invoices by company and supplier.

    This function orchestrates the full invoice processing pipeline:
        - convert the PDF into images (one image per page)
        - apply OCR with preprocessing (OpenCV + Pytesseract)
        - analyze each page (company, supplier, VAT,validation keyword)
        - detect two-page invoices aned concatenate images when necessary
        - validate invoices using a keyword check
        - resolve the output diectories (company / parrent / supplier)
        - Generate and save one classified PDF per invoice
        - Log results into a tracking CSV file

    The final directory structure under `output_dir` is typically:
    output_dir / <company> / <normalized_supplier> / invoice<timestamp>.pdf

    Side effects:
        - Creates directories (`suivi_dir`, `output_dir`, `archive_suivi_dir`) if missing
        - Saves intermediate PNG images extracted from the PDF
        - May overwrite images during two-page invoice concatenation
        - Writes classified invoice PDFs to disk
        - Appends metadata rows to a tracking CSV file via `suivi_resultat_csv`

    Args:
        input_pdf (str): Path to the input PDF file to process

        key_word (str): Validation keyword used to confirm that a page
        corresponds to a valid invoice. Defaults to `config.VALIDATION_KEYWORD`.

        suivi_dir (str):Root directory used to store intermediate files (e.g., extracted PNG images). 
        Defaults to `config.SUIVI_DIR`.

        archive_suivi_dir (str): Subdirectory used to archive extracted
        invoice pages. Defaults to `config.FACTURE_CLASSEES_DIR`.

        company_csv (pd.DataFrame): Company registry dataframe used to resolve company 
        and parent company directories.

        supplier_csv (pd.DataFrame): Supplier registry dataframe used to
        normalize and resolve supplier names. Defaults to config.supplier_df.

        list_company_invoice (list): Approved list of known company names
        used for direct matching. Defaults to config.LIST_COMPANY_NAME_INVOICE.

        output_dir (str): Root output directory where classified invoices will be saved.
        Defaults to config.OUTPUT_DIR.

        list_supplier (list): List of known suppliers used for detection.

        list_tva_supplier (list): List of known supplier TVA numbers used
        for TVA-based matching. Defaults to config.LIST_TVA_SUPPLIER.

        new_supplier (str): Default supplier name used if no match is found. Defaults to config.NEW_SUPPLIER.
    
        new_company (str): Default company name used if no match is found. Defaults to config.NEW_COMPANY.

    return

        None : this function does not explicitly return a value
        Results are written to disk and logged in the tracking CSV file

    Raises:
        FileNotFoundError: If `input_pdf` does not exist.
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
    two_page_invoice_list = []
    
    solo_page_invoice_list = []
    # solo_page_image_invoice_list = []
    used_indexes = set()
    page_list = []
    # two_page_image_invoice_list = []
    two_page_invoice_list_final = []
    
    #invoice final list
    invoice_list = []
    
    #dictionnary_list for the page:
    row_list = []
    row = {}
    
    #convert pdf into image
    images = convert_pdf_to_PIL(input_pdf)
    
    
    # loop for the scan of the page's image 
    for i,image in enumerate(images):

        print(f"******************************** {i}")
        print('--------------------------------------------------------------------------------------------------------------------------------------------')

        # conversion of pdf format into PNG format and save the image
        image_filename = f"{os.path.basename(input_pdf)}_{i+1}.png"
        archive_image_path = os.path.join(suivi_dir,archive_suivi_dir,image_filename)
        image.save(archive_image_path)
        logging.info("l'image est enregistré dans : %s",archive_image_path)
        # row['train_image_path'] = archive_image_path

        text_ocr = image_to_text(path=archive_image_path,
                                 config_tesseract=config.PYTESSERACT_CONFIG,
                                 index=i)[1]
    
    # -------------------------- invoice detection--------------------------
    #cleaning text from pytesseract OCR
        # text_ocr = clean_text(text)
    
        page = analyse_invoice_page(image_path=archive_image_path,
                                    clean_text_ocr=text_ocr,
                                    company_df=company_csv,
                                    supplier_list=list_supplier,
                                    tva_supplier_list=list_tva_supplier,
                                    new_company=new_company,
                                    key_word=key_word,
                                    position=i)
    
        page_list.append(page)
    
    #detection of 2 pages invoice and one page invoice
    
    two_page_invoice_list, used_indexes = detection_two_page_invoice(page_list)
    

    #solo page invoice
    
    solo_page_invoice_list = detection_one_page_invoice(page_list = page_list,
                                                        used_indexes = used_indexes)
    
    #invoice 2-page concatenation
    
    two_page_invoice_list_final = concat_invoice_two_page(two_page_invoice_list)
        
    directory_company_path = None
    # directory_parent_company = None
    # row = {}


    invoice_list = solo_page_invoice_list + two_page_invoice_list_final
    
    logging.info(f"invoice_list: {invoice_list}")
    
    for i,invoice in enumerate(invoice_list):
        
        #preprocessing image +  #convert image to string
        
        image_invoice,clean_text_ocr_invoice = image_to_text(path = invoice[config.PATH],
                                               config_tesseract = config.PYTESSERACT_CONFIG,
                                               index = i)

        if check_invoice(text=clean_text_ocr_invoice,key_word=key_word):
                       
            logging.info(f"{invoice['path']}")
            row={}
            
            #----------feature train_image_path------------
            
            row['train_image_path'] = os.path.basename(invoice['path'])

            directory_company_path = None
            directory_parent_company = None
            # clean_text_ocr = clean_text(text)

            #----- COMPANY DETECTION------------------------
            company_name = check_company(text=clean_text_ocr_invoice,
                                         company_df=company_csv,
                                         new_company=new_company)
            
            logging.debug("Detected company name : %s", company_name)

            if isinstance(company_name,tuple):
                row['parent_company']=company_name[0]
            else:
                row['parent_company']= 0
            
            
            #--------------company and parent company path ----------------------
            

            directory_company_path = resolve_company_path(company_csv = company_csv,
                                                     company_name = company_name,
                                                     output_dir = output_dir,
                                                     list_company_invoice = list_company_invoice,
                                                     new_company = new_company)
            
            row[company_name] = os.path.basename(directory_company_path)

            #--------------supplier detection and check with TVA----------------------
            
            norm_name = resolve_supplier_path(clean_text_ocr_invoice = clean_text_ocr_invoice,
                                              list_supplier = list_supplier,
                                              list_tva_supplier = list_tva_supplier,
                                              supplier_csv = supplier_csv)
            
            #--------------invoice path creation-----------------------    
        

            dir_path_supply = make_directory_supply(directory_company=directory_company_path,directory_supplier=norm_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            invoice_path = os.path.join(dir_path_supply,f"facture{timestamp}.pdf")
            
            #----------convert_pdf_format + sauvegarde ------------
            
            max_size = (1654, 2339) #200 DPI
            image_from_array = Image.fromarray(image_invoice)
            image_rgb = image_from_array.convert('RGB')
            image_rgb.thumbnail(max_size,Image.Resampling.LANCZOS)
            image_rgb.save(invoice_path,"PDF",resolution=300)
            
            #--------feature supplier_name-------------
            row['supplier_name'] = norm_name

            row_list.append(row)

            #-------------sauvegarde de la row dans le fichier suivi.csv----------------

            suivi_resultat_csv(file_path=invoice_path,row=row)
            
        
        else:
            logging.warning("no validation key on the invoice ")


        #-------------Fin sauvegarde de la row_list dans le fichier suivi.csv----------------
        
