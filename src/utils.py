import os
import re
import pytesseract
from pdf2image import convert_from_path
from config import OUTPUT_DIR #,LIST_COMPANY,INPUT_PDF

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
                  company_list_name_invoice_guillaume,
                  company_list_tva_guillaume,
                  company_list_name_invoice,
                  company_list_tva):
    """check

    Args:
        text (str): _description_
        company_list_name_invoice (_type_): _description_
        company_list_name_registery (_type_): _description_
    """
    clean_text = text.lower().replace(" ","").replace("-","")

    # for company_name_gui,tva_company_gui in zip(company_list_name_invoice_guillaume,
    #                                             company_list_tva_guillaume):
    #       if company_name_gui.lower().replace(" ","") in clean_text:
    #           return company_name_gui
    #       elif tva_company_gui.lower().replace(" ", "") in clean_text:
    #           return 'new_company_gui'
          
    for company_name,tva_company in zip(company_list_name_invoice,company_list_tva):
        if (company_name.lower().replace(" ","") in clean_text or 
            tva_company.lower().replace(" ","") in clean_text ):
            return company_name

    return 'new_company'


def check_supplier(text:str,
                   supplier_list:list,
                   tva_supplier_list:list):
    """
    check the company name in the invoice

    return
        company name or None

    """    
    clean_text = text.lower().replace(" ","").replace("-","")
    
    for supplier_name,tva_supplier in zip(supplier_list,tva_supplier_list):
        if (supplier_name.lower().replace(" ","") in clean_text or 
            tva_supplier.lower().replace(" ","") in clean_text 
            ):
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
    

