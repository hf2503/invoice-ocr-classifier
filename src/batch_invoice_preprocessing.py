""" 
This modules do the following actions:

  - 'archive_csv ' :Ensure the tracking and archiving of pdf files containing invoices
  
  
  - 'batch_invoice_preprocessing' : 
        It's the entry point of the pdf files with numerous invoices, this founction do :

        - scan an input folder for pdf
        - check the if the pdf file has been processed
        - call 'archive_csv' to save the pdf file in a folder track and csv file track
        - call process_invoice_pdf for OCR classification
        - move processed invoice to an archive folder or delete the processed invoice if it already exists in the archive folder).
"""

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

def archive_csv(file_path,
                csv_path=config.ARCHIVE_CSV,
                columns=config.COLUMNS_SUIVI_BRUTE):
    """

    This function ensure the tracking of the raw pdf file (date,time and SHA1)

    Args:
        file_path (str): Path of the raw pdf file
        csv_path (str): Path the archive csv file. Defaults to config.ARCHIVE_CSV.
        columns (list[str]): csv headers if the file doesn't exist . Defaults to config.COLUMNS_SUIVI_BRUTE.


    returns 

        None : writes in a tracking folder  

    
    side Effects:

        - creates the parent directory if it doesn't exist
        - open and appends to a csv file on disk (delimiter=';', encoding = 'utf8')
        - produces log messages


    """

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
    """

    Ingest pdf invoice from an input folder (input_pdf_folder)
    
    workflow :
    
        - Ensure that input folder, archive folder exist
        - Ensure that input folder is not empty
        - List the pdf file in input folder and list the pdf files in archive folder
        - For each new pdf file :
                    - call 'process_invoice_pdf' to run OCR, classification, filing
                    - Move processed pdf invoice to tracking folder and tracking csv file if 
                    the pdf invoice already exist , the pdf file is deleted
    
    
    
    Args:
        input_pdf_folder (str): Path to the folder who contains the raw pdf file. Defaults to config.INPUT_DIR.
        archive_input_pdf_folder (str): Path to the root archive directory who contains the folder for archieve raw pdf processed and csv file for the tracking. Defaults to config.ARCHIVE_DIR.
        raw_invoice_folder (str): Path to the subdirectory under the archive root who contains the raw pdf processed . Defaults to config.FACTURES_BRUTES_DIR.

    Returns:
       None
       
    Side Effects:
            - creates folder if they don't exist
            - Moves or removes files
            - Appends a row to the archive_tracking csv
            - call 'process_invoice_pdf' witch perform OCR and write some files
        
        
    """




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
    
    # scan du dossier contenant les fichiers à traiter
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

