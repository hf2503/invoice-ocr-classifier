import pytesseract
from datetime import datetime
import os
import logging
import config
from utils import *


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

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

def process_invoice_pdf(input_pdf:str,
                        company_csv = config.company_df,
                        company_invoice=config.LIST_COMPANY_NAME_INVOICE,
                        company_directory=config.LIST_COMPANY_NAME_DIRECTORY,
                        company_tva = config.LIST_COMPANY_TVA,
                        output_dir= config.OUTPUT_DIR,
                        supplier= config.LIST_SUPPLIER,
                        tva_supplier_list= config.LIST_TVA_SUPPLIER,
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
    
    
    images = convert_pdf_to_PIL(input_pdf)
    
    for i,image in enumerate(images):
        
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            
            logging.error("L'OCR pytesseract failed on page %d of file %s: %s", i+1,os.path.basename(input_pdf),e)
            continue
        
        
        if check_invoice(text):

            #company detection
            company_name = check_company(text,
                                         company_list_name_invoice=company_invoice,
                                         company_list_tva=company_tva
                                         )
            

            logging.debug("Detected company name : %s", company_name)


            directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values
            
            if len(directory_company_match):
                print(directory_company_match)
                directory_company = directory_company_match[0]   
                directory_company_path = make_directory_company(output_dir,directory_company)
                logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                print(directory_company_path)
            
            else:
                logging.warning("company name '%s' not found in registry; fallback to '%s'",company_name,new_company)
                directory_company_path = make_directory_company(output_dir,new_company)



            #supplier detection
            supplier_name = check_supplier(text,supplier_list=supplier,tva_supplier_list=tva_supplier_list)

            if supplier_name:
                norm_name = normalise_supply_name(text = supplier_name)

            else:
                norm_name = normalise_supply_name(text =new_supplier)
            
            dir_path_supply = make_directory_supply(directory_company=directory_company_path,directory_supplier=norm_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            invoice_path = os.path.join(dir_path_supply,f"facture{timestamp}.pdf")
            image.convert('RGB').save(invoice_path)
            logging.info("invoice save to : %s",invoice_path)
     
        else:
            logging.info("invoice's page rejected ")