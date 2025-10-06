import pandas as pd
import os
import platform
from dotenv import load_dotenv
load_dotenv()


#project_path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,'data')
INPUT_DIR = os.path.join(DATA_DIR,'factures_brutes')
OUTPUT_DIR = os.path.join(DATA_DIR,'factures_classees')
ARCHIVE_DIR = os.path.join(DATA_DIR,'factures_brutes_archivees')
SUIVI_DIR = os.path.join(DATA_DIR,'suivi')

#csv path
SUPPLIER_LIST_CSV = os.path.join(DATA_DIR,"list_supplier.csv")
COMPANY_LIST_CSV = os.path.join(DATA_DIR,"list_company.csv")
ARCHIVE_CSV = os.path.join(ARCHIVE_DIR,'facture__brutes_archivees.csv')
SUIVI_CSV = os.path.join(SUIVI_DIR,'suivi.csv')


#A supprimer
TRAIN_FINAL = os.path.join(BASE_DIR,"train_final",'dataset')

#read csv
df = pd.read_csv(SUPPLIER_LIST_CSV ,sep=',')
company_df = pd.read_csv(COMPANY_LIST_CSV,sep=',')


LIST_COMPANY_NAME_INVOICE = list(company_df['company_name_invoice'])
LIST_COMPANY_NAME_DIRECTORY = list(company_df['company_name_registery'])
LIST_COMPANY_TVA = list(company_df['ID_TVA'])

#LIST_COMPANY_NAME_INVOICE_GUILLAUME = list(company_guillaume['company_name_invoice'])
#LIST_COMPANY_NAME_DIRECTORY_GUILLAUME = list(company_guillaume['company_name_registery'])
#LIST_COMPANY_TVA_GUILLAUME = list(company_guillaume['ID_TVA'])
PARENT_COMPANY = 'SPG'


LIST_SUPPLIER = list(df['entreprise'])
LIST_TVA_SUPPLIER = list(df['ID_TVA'])

# LIST_NEW_SUPPLIER = list(dg['entreprise'])
# LIST_TVA_NEW_SUPPLIER = list(dg['ID_TVA'])


#tesseract_path
system = platform.system()

if system == 'Windows':
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_WIN", "tesseract")

else:
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_LINUX", "tesseract")
    

#constant
NEW_SUPPLIER = "new_supplier"
NEW_COMPANY = "new_company"





