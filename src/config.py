import pandas as pd
import os
import platform
from dotenv import load_dotenv
load_dotenv()


#project_path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,'data')
INPUT_DIR = os.path.join(DATA_DIR,'factures_brutes_a_traiter')
OUTPUT_DIR = os.path.join(DATA_DIR,'factures_classees')
ARCHIVE_DIR = os.path.join(DATA_DIR,'factures_brutes_archivees')
SUIVI_DIR = os.path.join(DATA_DIR,'suivi')

#dossier facture classé (format png) et dossier facture brutes (format pdf)
FACTURE_CLASSEES_DIR = os.path.join(SUIVI_DIR,'factures_traitees_archive')
FACTURES_BRUTES_DIR = os.path.join(ARCHIVE_DIR,'factures_brutes')

#csv path
SUPPLIER_LIST_CSV = os.path.join(DATA_DIR,"list_supplier.csv")
COMPANY_LIST_CSV = os.path.join(DATA_DIR,"list_company.csv")
ARCHIVE_CSV = os.path.join(ARCHIVE_DIR,'factures__brutes_archivees.csv')
SUIVI_CSV = os.path.join(SUIVI_DIR,'suivi_factures_traitees.csv')
RESULTAT_CSV = os.path.join(OUTPUT_DIR,'resultat.csv')

#read csv
df = pd.read_csv(SUPPLIER_LIST_CSV ,sep=',')
company_df = pd.read_csv(COMPANY_LIST_CSV,sep=',')


LIST_COMPANY_NAME_INVOICE = list(company_df['company_name_invoice'])
LIST_COMPANY_NAME_DIRECTORY = list(company_df['company_name_registery'])
LIST_COMPANY_TVA = list(company_df['ID_TVA'])
PARENT_COMPANY = 'SPG'

#Colonnes suivi.csv et facture_brutes_archivees.csv
COLUMNS_SUIVI_BRUTE = ['facture_brute','date','heure','sha1_pdf']
COLUMNS_SUIVI = ['facture_traitee','parent_company','company_name','supplier_name','date','sha1_pdf']


LIST_SUPPLIER = list(df['entreprise'])
LIST_TVA_SUPPLIER = list(df['ID_TVA'])


#tesseract_path
system = platform.system()

if system == 'Windows':
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_WIN", "tesseract")

else:
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_LINUX", "tesseract")
    

#constant
NEW_SUPPLIER = "new_supplier"
NEW_COMPANY = "new_company"





