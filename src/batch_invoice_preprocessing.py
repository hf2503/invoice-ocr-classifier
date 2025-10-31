import os
import traceback
import shutil
import logging
from datetime import datetime
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

def clear_folder():
    pass









def archive_csv(file_path,
                csv_path=config.ARCHIVE_CSV,
                columns=config.COLUMNS_SUIVI_BRUTE):


    #vérification que le dossier archive_brute.csv existe
    os.makedirs(os.path.dirname(csv_path),exist_ok=True)

    filename = os.path.basename(file_path)
    logging.info(f"filename : {filename}")
    
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    heure = now.strftime("%H-%M")
    pdf_hash = extract_SHA1(file_path)
    
    #valeur pour écriture
    values = [filename,date,heure,pdf_hash]
    
    #on test si le csv existe
    file_exists = os.path.exists(csv_path)

    with open(csv_path,'a',newline='',encoding='utf-8') as f:
        writer = csv.writer(f,delimiter=';')
        if not file_exists : 
            writer.writerow(columns)
        writer.writerow(values)


def batch_invoice_preprocessing(input_pdf_folder = config.INPUT_DIR,
                                archive_input_pdf_folder = config.ARCHIVE_DIR,
                                raw_invoice_folder = config.FACTURES_BRUTES_DIR,
                                ):
    
    #vérification de l'existence du dossier data/facture brutes
    os.makedirs(input_pdf_folder,exist_ok=True)

    #vérification de l'exitence du dossier facture brutes archivees
    os.makedirs(archive_input_pdf_folder,exist_ok=True)
    
    #verification de l'existence du dossier facture brute
    os.makedirs(raw_invoice_folder,exist_ok=True)

    list_pdf_input_folder = os.listdir(input_pdf_folder)

    already_archived = set(os.listdir(raw_invoice_folder))
        
    if len(list_pdf_input_folder)==0:
        print("there are not invoices into the directory input")
        return None
    
    
    for filename in list_pdf_input_folder:

        if not filename.endswith('.pdf'):
            logging.info(f"le fichier {filename} doit être au format pdf")
            continue


        if filename in already_archived:
            print("le fichier a déjà été traité")
            continue

            
            #enregistrement dans le fichier archive_facture.csv

        file_path = os.path.join(input_pdf_folder,filename)
        logging.info("input_pdf_folder:%s:",file_path)
        archive_csv(file_path)
            
        try:
            process_invoice_pdf(input_pdf=file_path)

            #sauvegarde du fichier pdf brut dans un le dossier  facture brute archive
            archive_path = os.path.join(archive_input_pdf_folder,raw_invoice_folder,filename)


            logging.info(f"le fichier brute pdf {filename} a été traité avec succés")
                
            if not os.path.exists(archive_path):
                shutil.move(file_path,archive_path)

            else:
                logging.warning("l'archive existe déjà")
                    #pas de deplacement et supression du fichier brute traité

                logging.debug(f"le fichier à supprimer est : {file_path}")
                os.remove(file_path)

        except Exception as e:
            print(f"on eu l'erreur suivante avec le fichier {filename} : {e}")
            traceback.print_exc()

