import os
import traceback
# import config
import logging

from . import config
from .process_invoice_pdf import process_invoice_pdf
# from reclassify_unidentified_invoices import reclassify_unidentified_invoices

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)


def batch_invoice_preprocessing(input_pdf_folder = config.INPUT_PDF_FOLDER):
    list_pdf_input_folder = os.listdir(input_pdf_folder)
    
    for filename in list_pdf_input_folder:
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(input_pdf_folder,filename)
            logging.info("input_pdf_folder:%s:",input_pdf_folder)
            
            try:
                process_invoice_pdf(input_pdf=input_pdf_path)
            except Exception as e:
                print(f"on eu l'erreur suivante avec le fichier {filename} : {e}")
                traceback.print_exc()
        else:
            raise TypeError(f"le fichier {filename} doit être au format pdf")
