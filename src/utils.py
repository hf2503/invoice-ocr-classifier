import pandas as pd
import unicodedata
import os
import re
import pytesseract
from pdf2image import convert_from_path
from config import OUTPUT_DIR #,LIST_COMPANY,INPUT_PDF
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)


def convert_pdf_to_PIL(input_pdf:str):
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"the file {input_pdf} doesn't exist")
    
    if not input_pdf.endswith('.pdf'):
        raise ValueError(f"the file{input_pdf} is not a pdf")
    
    image = convert_from_path(input_pdf)
    return image


def check_invoice(text):
    """
    check the invoice's page where "verifie le " is written

    Args:
        text (str): ten invoice's text

    Returns:
        True or False
    """
    return "verifie le" in text.lower()

def check_company(text:str,
                  company_df:pd.DataFrame,
                  company_list_name_invoice: list,
                  company_list_tva: list,
                  new_company: str):
    """check

    Args:
        text (str): _description_
        company_list_name_invoice (_type_): _description_
        company_list_name_registery (_type_): _description_
    """
    
 
    
    text = text.lower()
    clean_text = unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('utf-8')
    # text = text.replace("-", " ").replace("_", " ")
    # clean_text = text.strip()
    

    # if company_df.isna().sum() > 0:
    #     company_df = company_df.fillna('0')
    #     logging.warning()

    
    for index, row in company_df.iterrows():
        company_name_invoice = row['company_name_invoice'].lower().replace(" ","").replace("-","").replace("_","")
        tva_company = row['ID_TVA'].lower().replace(" ","")
        parent_company = row.get('parent_company',"")
        logging.info("parent_company : %s",parent_company)

        if company_name_invoice in clean_text or tva_company in clean_text:
            if parent_company!="0":
                #we take back row['company_name_invoice'] because we need the raw name
                return (parent_company,row['company_name_invoice'])
            else:
                return row['company_name_invoice']
    
    return new_company


def check_supplier(text:str,
                   supplier_list:list,
                   tva_supplier_list:list):
    """
    check the company name in the invoice

    return
        company name or None

    """    
    text = text.lower()
    text = unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode('utf-8')
    text = text.replace("-", " ").replace("_", " ")
    clean_text = text.strip()
    

    
    for supplier_name,tva_supplier in zip(supplier_list,tva_supplier_list):
        if (supplier_name.lower().replace(" ","") in clean_text or 
            tva_supplier.lower().replace(" ","") in clean_text 
            ):
            print(tva_supplier.lower())
            return supplier_name
    
    return None



def normalise_supply_name(text):
    """
    preprocess the companies name directory

    Args:
        text (str): company's name

    Returns:
        text
    """
    
    text = text.strip()
    text = re.sub(r'[<>:"/\\|?*]','',text)
    text = text.replace(' ','_')
    return text


def make_directory_company(output_dir,directory):
    """
    Create a directory if it doesn't exist.

    Args:
        directory (str): The path of the directory to be created.

    Returns:
        path
    """
    path = os.path.join(output_dir,directory)
    print(path)
    
    if not (os.path.exists(path)):
        os.makedirs(path)
        print(f"dossier {directory} créé")
        return path
    else:
        print(f"dossier {directory} déjà existant")
        return path


def make_directory_mother_company(output_dir,mother_company,directory):
    """
    Create a directory if it doesn't exist.

    Args:
        directory (str): The path of the directory to be created.

    Returns:
        path
    """
    path = os.path.join(output_dir,mother_company,directory)
    print(path)
    
    if not (os.path.exists(path)):
        os.makedirs(path)
        print(f"dossier {directory} créé")
        return path
    else:
        print(f"dossier {directory} déjà existant")
        return path



def make_directory_supply(directory_company,directory_supplier):
    """
    Create a directory if it doesn't exist.

    Args:
        directory (str): The path of the directory to be created.

    Returns:
        path
    """
    path = os.path.join(directory_company,directory_supplier)
    print(path)
    
    if not (os.path.exists(path)):
        os.makedirs(path)
        print(f"dossier {directory_supplier} créé")
        return path
    else:
        print(f"dossier {directory_supplier} déjà existant")
        return path
    

