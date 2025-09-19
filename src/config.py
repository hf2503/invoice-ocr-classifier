import pandas as pd
import os
import platform
from dotenv import load_dotenv
load_dotenv()


#project_path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR,'data')
print(DATA_DIR)

INPUT_PDF_FOLDER = os.path.join(DATA_DIR,'input')
print(INPUT_PDF_FOLDER)
# INPUT_NEW_PDF_DIRECTORY = os.path.join()  

OUTPUT_DIR = os.path.join(DATA_DIR,'output')
print(OUTPUT_DIR)


#csv path
SUPPLIER_CSV = os.path.join(BASE_DIR,"data","supplier_copy.csv")
SUPPLIER_COPY_CSV = os.path.join(BASE_DIR,"data","supplier_copy.csv")
COMPANY_LIST_CSV = os.path.join(BASE_DIR,"data","list_company.csv")
#COMPANY_LIST_GUILLAUME_CSV = os.path.join(BASE_DIR,"data","list_company_guillaume.csv")

#database path for train:
TRAIN_DIR = os.path.join(BASE_DIR,"data","train")
TRAIN_FINAL = os.path.join(BASE_DIR,"train_final",'dataset')

#read csv
df = pd.read_csv(SUPPLIER_CSV,sep=',')
dg = pd.read_csv(SUPPLIER_COPY_CSV,sep=',')
company_df = pd.read_csv(COMPANY_LIST_CSV,sep=',')
#company_guillaume = pd.read_csv(COMPANY_LIST_GUILLAUME_CSV,sep=',')

LIST_COMPANY_NAME_INVOICE = list(company_df['company_name_invoice'])
LIST_COMPANY_NAME_DIRECTORY = list(company_df['company_name_registery'])
LIST_COMPANY_TVA = list(company_df['ID_TVA'])

#LIST_COMPANY_NAME_INVOICE_GUILLAUME = list(company_guillaume['company_name_invoice'])
#LIST_COMPANY_NAME_DIRECTORY_GUILLAUME = list(company_guillaume['company_name_registery'])
#LIST_COMPANY_TVA_GUILLAUME = list(company_guillaume['ID_TVA'])
PARENT_COMPANY = 'SPG'


LIST_SUPPLIER = list(df['entreprise'])
LIST_TVA_SUPPLIER = list(df['ID_TVA'])

LIST_NEW_SUPPLIER = list(dg['entreprise'])
LIST_TVA_NEW_SUPPLIER = list(dg['ID_TVA'])


#tesseract_path
system = platform.system()

if system == 'Windows':
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_WIN", "tesseract")

else:
    TESSERACT_PATH = os.getenv("TESSERACT_PATH_LINUX", "tesseract")
    

#constant
NEW_SUPPLIER = "new_supplier"
NEW_COMPANY = "new_company"





