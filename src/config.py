import pandas as pd
import os

#project_path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


#csv path
SUPPLIER_CSV = os.path.join(BASE_DIR,"data","supplier.csv")
SUPPLIER_COPY_CSV = os.path.join(BASE_DIR,"data","supplier_copy.csv")
COMPANY_LIST_CSV = 

#read csv
df = pd.read_csv(SUPPLIER_CSV,sep=',')
dg = pd.read_csv(SUPPLIER_COPY_CSV,sep=',')
company_df = pd.read_csv('../data/list_company.csv')

LIST_COMPANY_NAME_INVOICE = list(company_df['company_name_invoice'])
LIST_COMPANY_NAME_REGISTERY = list(company_df['company_name_registery'])

LIST_SUPPLIER = list(df['entreprise'])
LIST_TVA_SUPPLIER = list(df['ID_TVA'])

LIST_NEW_SUPPLIER = list(dg['entreprise'])
LIST_TVA_NEW_SUPPLIER = list(dg['ID_TVA'])

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

INPUT_PDF_FOLDER = "../data/input"
OUTPUT_DIR = "../data/output"

NEW_SUPPLIER = "new_supplier"
INPUT_NEW_SUPPLIER_PDF = "../data/output/new_supplier"

