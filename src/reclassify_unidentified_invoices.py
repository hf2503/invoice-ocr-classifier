import config
from utils import *
from datetime import datetime
import pytesseract
import logging



# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)



def reclassify_unidentified_invoices(input_new:str,
                                              new_company_list=config.LIST_NEW_SUPPLIER,
                                              tva_new_supplier_list=config.LIST_TVA_NEW_SUPPLIER,
                                              new_supplier=config.NEW_SUPPLIER):
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