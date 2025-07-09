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
    
    
    images = convert_pdf_to_PIL(input_pdf)
    
    for i,image in enumerate(images):
        
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            
            logging.error("L'OCR pytesseract failed on page %d of file %s: %s", i+1,os.path.basename(input_pdf),e)
            continue
        
        
        if check_invoice(text):

            directory_company_path = None
            directory_parent_company = None
            clean_text_ocr = clean_text(text)
            #company detection
            company_name = check_company(clean_text_ocr,
                                         company_df=company_csv,
                                         company_list_name_invoice=list_company_invoice,
                                         company_list_tva=list_company_tva,
                                         new_company=new_company
                                         )
            

            logging.debug("Detected company name : %s", company_name)

            print(f"company name : {company_name}")

            if isinstance(company_name, tuple) :

                directory_parent_match = company_csv.loc[company_csv['parent_company'] == company_name[0],'parent_company'].values
                directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name[1],'company_name_registery'].values
                
                if directory_company_match.size > 0:

                    logging.info("directory_company_match: %s",directory_company_match)

                    directory_parent_company = directory_parent_match[0]

                    logging.info("directory_parent_company:%s:",directory_parent_company)

                    directory_company = directory_company_match[0]  

                    logging.info("ddirectory_company:%s:",directory_company)

                    directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)

                    logging.info("directory_company_path:%s:",directory_company_path)

                    logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                    print(directory_company_path)
                
                else:
                    logging.info("company_name[1] : %s",company_name[1])
                    logging.info("company_name[0] : %s",company_name[0])
                    logging.info("company name '%s' not found in registry; fallback to '%s'",company_name[0],company_name[1])
                    directory_parent_company = company_name[0]
                    directory_company = company_name[1]
                    directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,company_name[1])


            elif company_name in list_company_invoice or company_name == 'new_company':
                directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values
                if directory_company_match.size > 0:
                    print(directory_company_match)
                    directory_company = directory_company_match[0]   
                    directory_company_path = make_directory_company(output_dir,directory_company)
                    logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
                    print(directory_company_path)
                else:
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
            image.convert('RGB').save(invoice_path)
            logging.info("invoice save to : %s",invoice_path)
     
        else:
            logging.info("invoice's page rejected ")