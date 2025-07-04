
import pytesseract
from datetime import datetime
import matplotlib.pyplot as plt
import os
from config import *
from utils import *
import traceback
import logging


print(f"Tesseract path loaded: {TESSERACT_PATH}")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)

#desactivate the debug message of pillow in the file invoice_processing.log
logging.getLogger('PIL').setLevel(logging.WARNING)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def convert_invoice_pdf(input_pdf:str,
                        company_csv = company_df,
                        company_invoice=LIST_COMPANY_NAME_INVOICE,
                        company_directory=LIST_COMPANY_NAME_DIRECTORY,
                        company_tva = LIST_COMPANY_TVA,
                        output_dir=OUTPUT_DIR,
                        supplier=LIST_SUPPLIER,
                        tva_supplier_list=LIST_TVA_SUPPLIER,
                        new_supplier=NEW_SUPPLIER,
                        new_company=NEW_COMPANY
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


def reclassify_from_the_directory_new_company(input_new:str,
                                              new_company_list=LIST_NEW_SUPPLIER,
                                              tva_new_supplier_list=LIST_TVA_NEW_SUPPLIER,
                                              new_supplier=NEW_SUPPLIER):
    """reclassify the invoice in the director
    when the csv LIST_SUPPLIER is update

    Raises:
        TypeError: _description_
    """
    
    
    if os.listdir(input_new):
        logging.info("found directories in input:%s",os.listdir(input_new))
        list_direcories_input = os.listdir(input_new)
        for directory in list_direcories_input:
            path_directory_supply = os.path.join(input_new,directory)
            list_directories_supply = os.listdir(path_directory_supply)
            
            for new_s in list_directories_supply:
                if new_s ==  new_supplier:
                    path_directory = os.path.join(path_directory_supply,new_s)
                    list_directories_new_supply = os.listdir(path_directory)
                    
                    for supplier in list_directories_new_supply:
                        logging.debug("the supplier list is : %s",os.listdir(path_directory))
                        new_path = os.path.join(path_directory,supplier)
                        image = convert_pdf_to_PIL(new_path)
                        
                        try:
                            new_text = pytesseract.image_to_string(image[0])
                        except Exception as e:
                            logging.error("OCR error on file %s: %s", new_path, e)
  
                        new_supply = check_supplier(new_text,new_company_list,tva_new_supplier_list)
                        logging.debug("detected supplier : %s",new_supply)
                        if new_supply:
                            norm_new_text = normalise_supply_name(new_supply)
                            dir_new_path = make_directory_company(path_directory_supply,norm_new_text)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            new_invoice_path = os.path.join(dir_new_path,f"facture_{timestamp}.pdf")
                            image[0].convert('RGB').save(new_invoice_path)
                        #delete the pdf file
                            os.remove(new_path)
                            logging.info("file %s moved and removed",new_path)
            
            else :
                logging.warning("Supplier not identified for file %s", new_path)
                continue
            
    else:
        logging.info("No new companies found in input directory.")
        return None
                                  
                
if __name__ == "__main__":
    
    list_pdf_input_folder = os.listdir(INPUT_PDF_FOLDER)
    for filename in list_pdf_input_folder:
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(INPUT_PDF_FOLDER,filename)
            
            try:
                convert_invoice_pdf(input_pdf=input_pdf_path)
            except Exception as e:
                print(f"on eu l'erreur suivante avec le fichier {filename} : {e}")
                traceback.print_exc()
        else:
            raise TypeError(f"le fichier {filename} doit être au format pdf")
        
    reclassify_from_the_directory_new_company(input_new = OUTPUT_DIR)

        