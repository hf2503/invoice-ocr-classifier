import pandas as pd
import os
import platform
from dotenv import load_dotenv
load_dotenv()


# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,'data')
INPUT_DIR = os.path.join(DATA_DIR,'raw_invoices_to_process')
OUTPUT_DIR = os.path.join(DATA_DIR,'classified_invoices')
ARCHIVE_DIR = os.path.join(DATA_DIR,'archived_raw_invoices')
SUIVI_DIR = os.path.join(DATA_DIR,'tracking')

#dossier facture classé (format png) et dossier facture brutes (format pdf)
FACTURE_CLASSEES_DIR = os.path.join(SUIVI_DIR,'processed_invoices_archive')
FACTURES_BRUTES_DIR = os.path.join(ARCHIVE_DIR,'raw_invoices')

#csv path
SUPPLIER_LIST_CSV = os.path.join(DATA_DIR,"supplier_list.csv")
COMPANY_LIST_CSV = os.path.join(DATA_DIR,"company_list.csv")
ARCHIVE_CSV = os.path.join(ARCHIVE_DIR,'archived_raw_invocies.csv')
SUIVI_CSV = os.path.join(SUIVI_DIR,'processed_invoices_tracking.csv')
RESULTAT_CSV = os.path.join(OUTPUT_DIR,'results.csv')

#read csv
supplier_df = pd.read_csv(SUPPLIER_LIST_CSV ,sep=',')
company_df = pd.read_csv(COMPANY_LIST_CSV,sep=',')

LIST_COMPANY_NAME_INVOICE = list(company_df['company_name_invoice'])
LIST_COMPANY_NAME_DIRECTORY = list(company_df['company_name_registery'])
LIST_COMPANY_TVA = list(company_df['ID_TVA'])
PARENT_COMPANY = 'SPG'

#Colonnes suivi.csv et facture_brutes_archivees.csv
COLUMNS_SUIVI_BRUTE = ['facture_brute','date','heure','sha1_pdf']
COLUMNS_SUIVI = ['facture_traitee','parent_company','company_name','supplier_name','date','sha1_pdf']


LIST_SUPPLIER = list(supplier_df['supplier_invoice'])
LIST_SUPPLIER_NAME_DIRECTORY = list(supplier_df['supplier_registery'])
LIST_TVA_SUPPLIER = list(supplier_df['TVA'])


#tesseract_path
system = platform.system()

if system == 'Windows':
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_WIN", "tesseract")

else:
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_LINUX", "tesseract")
    

#constant
NEW_SUPPLIER = "new_supplier"
NEW_COMPANY = "new_company"





