import pandas as pd
import unicodedata
from rapidfuzz import fuzz
import os
import re
import pytesseract
from pdf2image import convert_from_path
import logging

from .config import OUTPUT_DIR #,LIST_COMPANY,INPUT_PDF


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
    
    image = convert_from_path(input_pdf,dpi=300)
    return image


def clean_text(text:str):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)  # enlève accents
    text = text.encode('ascii', 'ignore').decode('utf-8')  # remove non-ascii
    text = text.replace("-", " ").replace("_", " ")  # standardise séparateurs
    text = re.sub(r"[^\w\s]", "", text)  # supprime ponctuation
    # text = re.sub(r"\s+", "", text)  # supprime tous les espaces (ou remplace par un espace si tu veux garder les mots)
    return text.strip()

    # text = str(text).lower()
    # text = unicodedata.normalize('NFKD', text)  # enlève accents
    # text = text.encode('ascii', 'ignore').decode('utf-8')  # remove non-ascii
    # text = text.replace("-", " ").replace("_", " ")  # standardise séparateurs
    # text = re.sub(r"[^\w\s]", "", text)  # supprime ponctuation
    # return text.strip()

def match_word(text:str,
               target:str):

    score_partial_ratio = fuzz.partial_ratio(text,target)

    return score_partial_ratio


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

    
    #--------------company without parent company--------------#
    
    company_no_parent = company_df[company_df['parent_company'].astype(str)=='0']
    
    #loop on company_no_parent
    for index, row in company_no_parent.iterrows():
        company_name_invoice = clean_text(row['company_name_invoice'])
        tva_company = clean_text(row['ID_TVA'])
        score_match_company = match_word(text,company_name_invoice)
        score_tva_company = match_word(text,tva_company)
        logging.info("company_name_loop : %s :, %s",company_name_invoice,score_match_company)
        
        if score_match_company > 92: #or score_tva_company ==100:
            return row['company_name_invoice']
        
    #----------------company with parent company---------------#
    
    company_with_parent = company_df[company_df['parent_company'].astype(str)!='0']
    
    #loop on company_with_parent
    for index, row in company_with_parent.iterrows():
        parent_company = row['parent_company']
        company_name_invoice = clean_text(row['company_name_invoice'])
        tva_company = clean_text(row['ID_TVA'])
        score_match_company = match_word(text,company_name_invoice)
        score_tva_company = match_word(text,tva_company)
        logging.info("company_name_loop : %s :, %s | parent_company : %s", company_name_invoice,score_match_company,parent_company)
        
        if score_match_company  > 90:
            return (parent_company, row['company_name_invoice'])
        
    return new_company
        
    
    # for index, row in company_df.iterrows():
    #     company_name_invoice = clean_text(row['company_name_invoice'])
    #     tva_company = clean_text(row['ID_TVA'])
    #     parent_company = row.get('parent_company',"")


    #     score_match_company = match_word(text,company_name_invoice)
    #     score_tva_company = match_word(text,tva_company)
    #     logging.info("company_name_loop : %s :, %s",company_name_invoice,score_match_company)



    #     if score_match_company ==100 or score_tva_company ==100:
    #         if pd.notna(parent_company) and str(parent_company) != "0":
    #             if pd.notna(row['company_name_invoice']):
    #                 return (parent_company, row['company_name_invoice'])   
    #             else:
    #                 logging.warning("Matched parent company but company_name_invoice is NaN.")
    #                 return new_company
    #         else:
    #             if pd.notna(row['company_name_invoice']):
    #                 return row['company_name_invoice']
    #             else:
    #                 logging.warning("Matched company but company_name_invoice is NaN.")
    #                 return new_company

    
    # return new_company


def check_supplier(text:str,
                   supplier_list:list,
                   tva_supplier_list:list):
    """
    check the company name in the invoice

    return
        company name or None

    """    

    for supplier_name,tva_supplier in zip(supplier_list,tva_supplier_list):
        clean_supplier_name = clean_text(supplier_name)
        clean_tva_supplier = clean_text(tva_supplier)

        score_match_supplier = match_word(text,clean_supplier_name)
        score_tva_supplier = match_word(text,clean_tva_supplier)
        #print(f"supplier_name :{supplier_name} : {score_match_supplier}")


        if (score_tva_supplier == 100 or score_match_supplier > 90 ):
            #logging.info("supplier_name:%s",supplier_name)
            #logging.info("tva_supplier:%s",tva_supplier)
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
    #print(path)
    
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
    

