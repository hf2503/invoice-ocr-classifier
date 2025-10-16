import pandas as pd
import unicodedata
from rapidfuzz import fuzz
import os
import re
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
import shutil

import logging
import hashlib


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

        score_match_company = match_word(text,company_name_invoice)

        # logging.info("company_name_loop : %s :, %s",company_name_invoice,score_match_company)
        
        if score_match_company > 92:
            logging.info("company_name_loop : %s :, %s",company_name_invoice,score_match_company)
            return row['company_name_invoice']

        
    #----------------company with parent company---------------#
    
    company_with_parent = company_df[company_df['parent_company'].astype(str)!='0']
    
    #loop on company_with_parent
    for index, row in company_with_parent.iterrows():
        parent_company = row['parent_company']
        company_name_invoice = clean_text(row['company_name_invoice'])

        score_match_company = match_word(text,company_name_invoice)

        # logging.info("company_name_loop : %s :, %s | parent_company : %s", company_name_invoice,score_match_company,parent_company)
        
        if score_match_company  > 90:
            logging.info("company_name_loop : %s :, %s | parent_company : %s", company_name_invoice,score_match_company,parent_company)
            return (parent_company, row['company_name_invoice'])

        
    return new_company


def check_supplier(text:str,
                   supplier_list:list):
    """
    check the company name in the invoice

    return
        company name or None

    """    
    list_score_supplier = []
    for supplier_name in supplier_list:
        clean_supplier_name = clean_text(supplier_name)

        score_match_supplier = match_word(text,clean_supplier_name)
        list_score_supplier.append((supplier_name,score_match_supplier))

        if score_match_supplier > 90 :
            logging.info("supplier_name:%s",supplier_name)
            return supplier_name
    
    logging.info(f"le score max trouvé est : supplier_name {max(list_score_supplier)[0]} pour un score de {max(list_score_supplier)[1]}")
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
    
def extract_SHA1(file_path):

    #création de l'insance de l'algorithme de hachage cryptographqiue
    h = hashlib.sha1()

    #Hachage du fichier
    with open(file_path,'rb') as f:
        data = f.read()
        h.update(data)
        return h.hexdigest()

def clear_result_and_raw(dir_path):

    if len(os.listdir(dir_path)) == 0 :
        print("le dossier des resultats est vide")
        return None

    for elmt in os.listdir(dir_path):
        elmt_path = os.path.join(dir_path,elmt)

        try :
            if os.path.isfile(elmt_path):
                os.remove(elmt_path)
            elif os.path.isdir(elmt_path):
                shutil.rmtree(elmt_path)
        
        except Exception as e:
            print(f"on a eu l'erreur suivante lors de la suppression de {elmt_path}:{e}")
        
    print(f"le contenu du dossier {dir_path} a été vidé avec succés")


