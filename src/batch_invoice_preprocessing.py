import os
import traceback
import shutil
import logging
import datetime
import csv

from . import config
from .utils import extract_SHA1
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


def archive_csv(file_path,csv_path=config.ARCHIVE_CSV):


    #vérification que le dossier archive_brute.csv existe
    os.makedirs(os.path.dirname(csv_path),exist_ok=True)

    filename = os.path.basename(file_path)
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    heure = now.strftime("%M-%M")
    pdf_hash = extract_SHA1(file_path)

    with open(file_path,'a',newline='') as f :
        writer = csv.writer(f,delimiter=';')
        writer.writerow([filename,date,heure,pdf_hash])






def batch_invoice_preprocessing(input_pdf_folder = config.INPUT_DIR,
                                archive_input_pdf_folder = config.ARCHIVE_DIR):


    #vérification de l'existence du dossier data/facture brutes
    os.makedirs(input_pdf_folder,exist_ok=True)

    #vérification de l'exitence du dossier facture brutes archives
    os.makedirs(archive_input_pdf_folder,exist_ok=True)

    list_pdf_input_folder = os.listdir(input_pdf_folder)
        
    if len(list_pdf_input_folder)==0:
        print("there are not invoices into the directory input")
        return None
    
    for filename in list_pdf_input_folder:
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(input_pdf_folder,filename)
            logging.info("input_pdf_folder:%s:",input_pdf_folder)
            
            try:
                process_invoice_pdf(input_pdf=input_pdf_path)

                #archivage du fichier brut 
                shutil.move(input_pdf_path,archive_input_pdf_folder)


            except Exception as e:
                print(f"on eu l'erreur suivante avec le fichier {filename} : {e}")
                traceback.print_exc()
        else:
            raise TypeError(f"le fichier {filename} doit être au format pdf")
