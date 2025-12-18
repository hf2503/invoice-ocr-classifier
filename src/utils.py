import pandas as pd
import numpy as np
import unicodedata
from rapidfuzz import fuzz
import os
import re
import cv2
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
import shutil
from PIL import Image

import logging
import hashlib

from . import config


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/invoice_processing.log',mode='a',encoding='utf_8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def convert_pdf_to_PIL(input_pdf:str):

    """
    Convert a pdf file into a list of PIL images (one per page)

    parameteres:

        input_pdf : (str) Absolute or relative path to the PDF file to convert

    Raises:
        FileNotFoundError: 
            if the provided file path does not exist

        ValueError:
            if the provided file is not a .pdf.

    Returns:
        list [PIL.Image]:
            List of PIL Image objects representing the pages of the pdf
    """


    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"the file {input_pdf} doesn't exist")
    
    if not input_pdf.endswith('.pdf'):
        raise ValueError(f"the file{input_pdf} is not a pdf")
    
    image = convert_from_path(input_pdf,dpi=300)
    return image

def resize_image_width(image: np,
                       new_width:int):
    
    
        try:
            
            w = image.shape[1]
            h = image.shape[0]
            new_height = int(h * new_width/w)
            new_image_resize = cv2.resize(image,(new_height,new_width))
            
            return new_image_resize
        
        except Exception as e:
            logger.info(f"la fonction resize_image_width a rencontré l'erreur suivante : {e}")
        



def clean_text(text:str):
    """_summary_

    Args:
        text (str): Input text to normalize


    Returns:
        str : Cleaned text
    """

    text = text.lower()
    text = unicodedata.normalize('NFKD', text)  # remove accents
    text = text.encode('ascii', 'ignore').decode('utf-8')  # remove non-ascii
    text = text.replace("-", " ").replace("_", " ")  # standardize séparators
    text = re.sub(r"[^\w\s]", "", text)  # drop ponctuation
    # text = text.replace(" ","").replace("\n","")

    return text.strip()


def match_word(text:str,
               target:str):
    """_summary_

    Args:
        text (str): OCR result + cleaned text
        target (str): text to compare against (reference name)


    Returns:
        float: partial_ratio score from rapidfuzz (0-100)
    """

    score_partial_ratio = fuzz.partial_ratio(text,target)

    return score_partial_ratio




def check_invoice(text:str,
                  key_word:str):
    """
    check the invoice's page where "verifie le " is written

    Args:
        text (str): invoice's text

    Returns:
        bool: True of False
    """
    

    key_word = clean_text(key_word)
    score_partial = fuzz.partial_ratio(key_word,text)
    
    if score_partial >= 80:
        logging.info(f"score of check_invoice is {score_partial}")
        return True
    else:
        logger.warning(f"score of check_invoice is {score_partial}")
        # logger.warning(f"text : {text}")



def check_company(text:str,
                  company_df:pd.DataFrame,
                  new_company: str):
    """
    Identify the name of company and the parent company referenced in the invoice text 

    the function tries two passes:

        - comapny without a parent company (parent_company == '0')
        - Company with a parent company (parent_company != '0')

    the function uses fuzzy string matching between each company name known (comapny_df)
    and the OCR text and returns the first match above a score threshold ( = 92)

    if not match is found , returns 'new_company'

    Args:
        text (str): Cleaned OCR text
        company_df (pd.DataFrame): DataFrame containing :
                                                        - company_name_invoice
                                                        - parent_company
        new_company (str): fallback label if no match

    Returns:
            str | tuple (str, str)
                Either a company name (str), a tuple (parent_company, child company)
                or the provided fallback label 'new_company
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


def check_supplier(ocr_text:str,
                   supplier_list:list):

    """
    Detect the supplier's name in the text OCR cleaned using the fuzzy matching.

    The detection of the supplier name depends of a score (fuzz partial ratio)

    if the score > 90 it returns the supplier name else return NONE and logs the best score

    Args:
        text (str): _description_
        supplier_list (list): _description_

    Returns:
        str or None
            the supplier name (with a threshol >90) or None
    """

    list_score_supplier_ocr = []
    for supplier_name in supplier_list:
        clean_supplier_name = clean_text(supplier_name)

        score_match_supplier_ocr = match_word(ocr_text,clean_supplier_name)
        
        list_score_supplier_ocr.append((supplier_name,score_match_supplier_ocr))
        

        if score_match_supplier_ocr > 90 :
            logging.info("supplier_name:%s",supplier_name)
            return supplier_name
    
    logging.info(f"le score max pour le supplier suivant ests : supplier_name {max(list_score_supplier_ocr)[0]} pour un score de {max(list_score_supplier_ocr)[1]}")
    
    return None


def check_tva_supplier(ocr_text:str,
                       list_supplier:list,
                       list_tva:str):
    """
    Detect the supplier's name in the text OCR cleaned using the fuzzy matching.

    The detection of the supplier name depends of a score (fuzz partial ratio)

    if the score of TVA > 95 it returns the supplier name else return NONE and logs the best score

    Args:
        text (str): _description_
        supplier_list (list): _description_

    Returns:
        str or None
            the supplier name (with a threshol >90) or None
    """
    list_score_tva_supplier = []
    
    #this text without space and line breaks make easier the tva's detection
    text_tva = ocr_text.replace(' ','').replace('\n','')
    
    for tva,supplier_name in zip(list_tva,list_supplier):
        
        # clean_supplier_name = clean_text(supplier_name)
        clean_tva = clean_text(tva)
        
        # text_tva = clean_tva.replace(' ','').replace('-','')
        
        score_match_tva_ocr = match_word(clean_tva,text_tva)
        
        # score_match_tva_text_without_space = match_word(clean_tva,text_tva)
        
        # logger.info(f"score_tva : {score_match_tva_ocr}")
        
        list_score_tva_supplier.append(score_match_tva_ocr)
        
        if score_match_tva_ocr >= 90:
                logging.info("supplier_name:%s , tva_supplier:%s",supplier_name,tva)
                return supplier_name

    
    logging.info(f"the score max_OCR found is : {supplier_name} with score_match tva {max(list_score_tva_supplier)}")
        


def normalise_supply_name(text:str):
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


def make_directory_company(output_dir:str,
                           directory:str):
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
        logger.info(f"dossier {directory} créé")
        return path
    else:
        logger.info(f"dossier {directory} déjà existant")
        return path


def make_directory_mother_company(output_dir:str,
                                  mother_company:str,
                                  directory:str):
    """
    Create a directory if it doesn't exist.

    Args:
        directory (str): The path of the directory to be created.

    Returns:
        path
    """
    path = os.path.join(output_dir,mother_company,directory)

    
    if not (os.path.exists(path)):
        os.makedirs(path)
        logger.info(f"dossier {directory} créé")
        return path
    else:
        logger.info(f"dossier {directory} déjà existant")
        return path



def make_directory_supply(directory_company:str,directory_supplier:str):
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
        logger.info(f"dossier {directory_supplier} créé")
        return path
    else:
        logger.info(f"dossier {directory_supplier} déjà existant")
        return path
    
def extract_SHA1(file_path:str):
    """
    Compute the SHA1 hash of a file
    Args:
        file_path (str): the path to the file

    Returns:
        str: hex digest string
    """

    #création de l'insance de l'algorithme de hachage cryptographqiue
    h = hashlib.sha1()

    #Hachage du fichier
    with open(file_path,'rb') as f:
        data = f.read()
        h.update(data)
        return h.hexdigest()

def clear_result_and_raw(dir_path:str):
    """
    Delete all files and subdirecories in a given directory

    Args:
        dir_path (str): path to the directory
        
    Returns:
            None
    """

    if len(os.listdir(dir_path)) == 0 :
        logger.info("le dossier est vide")
        return None

    for elmt in os.listdir(dir_path):
        elmt_path = os.path.join(dir_path,elmt)

        try :
            if os.path.isfile(elmt_path):
                os.remove(elmt_path)
            elif os.path.isdir(elmt_path):
                shutil.rmtree(elmt_path)
        
        except Exception as e:
            logger.info(f"on a eu l'erreur suivante lors de la suppression de {elmt_path}:{e}")
        
    logger.info(f"le contenu du dossier {dir_path} a été vidé avec succés")

def clear_result_csv(dir_path :str):
    """
    remove the file in csv format

    Args:
        dir_path (str): path to the directory who contents the files in format csv

    Returns:
        None
    """

    if len(os.listdir(dir_path)) == 0 :
        logger.info("pas de fichier resultat.csv à supprimer")
        return None
    
    for elmt in os.listdir(dir_path):
        elmt_path = os.path.join(dir_path,elmt)

        try:
            if os.path.isfile(elmt_path):
                os.remove(elmt_path)
        except Exception as e:
            logger.error(f"on a eu l'erreur suivante lors de la suprression du fichier {elmt_path} : {e} ")
    
    logger.info(f"le fichier {elmt_path} a été supprimée avec succés")

def analyse_invoice_page(image_path:str,
                         clean_text_ocr:str,
                         company_df:pd.DataFrame,
                         supplier_list:list,
                         tva_supplier_list:list,
                         new_company:str,
                         key_word:str,
                         position:int):

    page = {}
    
    page[config.COMPANY] = check_company(text=clean_text_ocr,
                                         company_df = company_df,
                                         new_company=new_company)
    
    page[config.SUPPLIER] = check_supplier(ocr_text=clean_text_ocr,
                                           supplier_list = supplier_list)
    
    page[config.KEY_WORD] = check_invoice(text = clean_text_ocr,
                                          key_word = key_word)
    
    page[config.TVA] = check_tva_supplier(ocr_text = clean_text_ocr,
                                          list_supplier = supplier_list,
                                          list_tva=tva_supplier_list)
    
    page[config.PATH] = image_path
    
    page[config.POSITION] = position
    
    return page


def detection_two_page_invoice(page_list:list):
    used_indexes = set()
    two_page_invoice_list = []
    
    for i,p1 in enumerate(page_list):
        if i in used_indexes:
            continue
        for j in range(i+1,len(page_list)):
            p2 = page_list[j]
            
            keyword_condition =  p1[config.KEY_WORD] != p2[config.KEY_WORD]
            
            same_supplier = p1[config.SUPPLIER] != None and (p1[config.SUPPLIER] == p2[config.SUPPLIER] or 
                                                        p1[config.TVA] == p2[config.SUPPLIER] or 
                                                        p1[config.TVA] == p2[config.TVA] or 
                                                        p1[config.TVA] == p2[config.SUPPLIER])
            
            position_close = abs(p1[config.POSITION] - p2[config.POSITION]) <=1
            
            if keyword_condition and same_supplier and position_close:
                two_page_invoice_list.append((p1,p2))
                used_indexes.add(p1[config.POSITION])
                used_indexes.add(p2[config.POSITION])
                
    return two_page_invoice_list, used_indexes


def detection_one_page_invoice(page_list:list,
                               used_indexes:set):
    
    solo_page_invoice_list = [one_page for one_page in page_list if one_page[config.POSITION] not in used_indexes]
    
    return solo_page_invoice_list
                
                
def concat_invoice_two_page(two_page_invoice_list : list):
    
    two_page_invoice_list_final = []
    
    for image in two_page_invoice_list :
        
        logging.info(image)
        
        img_page_1 = cv2.imread(image[0][config.PATH])
        img_page_2 = cv2.imread(image[1][config.PATH])
    
        #concatenation
        img_concat = cv2.vconcat([img_page_1,img_page_2])
        
        cv2.imwrite(image[0][config.PATH],img_concat)
        
        two_page_invoice_list_final.append(image[0])
        
    return two_page_invoice_list_final
    
    
def image_to_text(path:str,
                  config_tesseract:str,
                  index:int):
    
    #preprocessing image
    image_invoice = cv2.imread(path)
    img_gray = cv2.cvtColor(image_invoice,cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(img_gray  , 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    #convert image to string
    try:
        text_invoice = pytesseract.image_to_string(threshold_img  ,config=config_tesseract)
        clean_text_ocr_invoice = clean_text(text_invoice)
        return image_invoice , clean_text_ocr_invoice
    
    except Exception as e:
        logging.error("L'OCR pytesseract failed on page %d of file %s: %s", index+1,os.path.basename(path),e)
        

def resolve_company(company_csv:pd.DataFrame,
                    company_name,
                    output_dir:str,
                    list_company_invoice:list,
                    new_company:str) :
        
    if isinstance(company_name, tuple):
        parent_company = company_name[0]
        company_name = company_name[1]

        #directory_parent_match = company_csv.loc[company_csv['parent_company'] == company_name[0],'parent_company'].values
        directory_parent_match = company_csv.loc[company_csv['company_name_invoice'] == parent_company,'parent_company'].values
        directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values

        logging.info("directory_company_match_size LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s",directory_company_match.size)    
        logging.info("directory_parent_match_debogage_1 LBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB: %s",directory_parent_match)
        logging.info("directory_company_match_debogage_1 LCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC: %s",directory_company_match)

        if directory_company_match.size > 1 :
                
            directory_parent_company = directory_parent_match[0]

            logging.info("directory_parent_company:%s:",directory_parent_company)

            directory_company = directory_company_match[0]  

            logging.info("directory_company:%s:",directory_company)

            directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)

            return directory_company_path

        else:

            directory_parent_company = directory_parent_match[0]
            logging.info("direcory_parent_company LDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD: %s",directory_parent_company)

            directory_company = directory_company_match[0]
            logging.info("company_name LDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD: %s",directory_company)

            directory_company_path = make_directory_mother_company(output_dir,directory_parent_company,directory_company)

            return directory_company_path


    elif company_name in list_company_invoice or company_name == 'new_company':
        directory_company_match = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values


        if directory_company_match.size > 0:
            logging.info(f"directory_company_match : {directory_company_match}")   
        
            directory_company = directory_company_match[0]   
            directory_company_path = make_directory_company(output_dir,directory_company)
            logging.info("using directory for registered company '%s' : %s ",directory_company,directory_company_path)
            logging.info(directory_company_path)
        
        else :

            logging.info("company name '%s' not found in registry; fallback to '%s'",company_name,new_company)
            directory_company_path = make_directory_company(output_dir,new_company)
    
    else:
        logging.warning("company name '%s' not matched anywhere; fallback to '%s'", company_name, new_company)
        directory_company_path = make_directory_company(output_dir, new_company)









                
                
                
                
                
                
                