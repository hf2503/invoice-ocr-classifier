
import pytesseract
from datetime import datetime
import matplotlib.pyplot as plt
import os
from config import *
from utils import *




pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def convert_invoice_pdf(input_pdf:str,output_dir=OUTPUT_DIR,company_list=LIST_SUPPLIER,tva_company_list=LIST_TVA_SUPPLIER,NEW_SUPPLIER=NEW_SUPPLIER):
    """
    convert the Image PIL into pdf files

    Args:
        image : invoice image 
    """
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"le fichier {input_pdf} est introuvable")
    
    
    images = convert_pdf_to_PIL(input_pdf)
    
    for i,image in enumerate(images):
        
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"on eu l'erreur suivante avec l'OCR pytesseract sur la page {i+1} du fichier {os.path.basename(input_pdf)}: {e}")
            continue
        
        
        if check_invoice(text):
            company_name = check_supplier(text,supplier_list=company_list,tva_supplier_list=tva_company_list)

            if company_name:
                norm_name = normalise_company_name(text = company_name)

            else:
                norm_name = normalise_company_name(text = NEW_SUPPLIER)

            dir_path = make_directory_company(output_dir=output_dir,directory=norm_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image.convert('RGB').save(os.path.join(dir_path,f"facture{timestamp}.pdf"))
            print(f"facture{i+1}.pdf enregistré dans {dir_path}")

        
        else:
            print("Factures non validées")


def reclassify_from_the_director_new_company(input_new:str,output_dir=OUTPUT_DIR,new_company_list=LIST_NEW_SUPPLIER,tva_new_company_list=LIST_TVA_NEW_SUPPLIER):
    """reclassify the invoice in the director
    when the csv LIST_SUPPLIER is update

    Raises:
        TypeError: _description_
    """
    
    
    if os.listdir(input_new):
        for filename in os.listdir(input_new):
            new_path = os.path.join(input_new,filename)
            image = convert_pdf_to_PIL(new_path)
            try:
                new_text = pytesseract.image_to_string(image[0])
            except Exception as e:
                print(f"on eu l'erreur suivante avec l'OCR pytesseract sur le {filename} : {e}")
                
            NEW_SUPPLIER = check_supplier(new_text,new_company_list,tva_new_company_list)
            print(NEW_SUPPLIER)
            
            if NEW_SUPPLIER:
                norm_new_text = normalise_company_name(NEW_SUPPLIER)
                dir_new_path = make_directory_company(output_dir,norm_new_text)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image[0].convert('RGB').save(os.path.join(dir_new_path,f"facture_{timestamp}.pdf"))
                
                #delete the pdf file
                os.remove(new_path)
                print(f"suppression du fichier {new_path}")
            
            else :
                continue
            
    else:
        print("There aren't new companies")
        return None
                                  
                
if __name__ == "__main__":
    for filename in os.listdir(INPUT_PDF_FOLDER):
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(INPUT_PDF_FOLDER,filename)
            
            try:
                convert_invoice_pdf(input_pdf=input_pdf_path)
            except Exception as e:
                print(f"on eu l'erreur suivante avec le fichier {filename} : {e}")
        else:
            raise TypeError(f"le fichier {filename} doit être au format pdf")
                
    reclassify_from_the_director_new_company(input_new = INPUT_NEW_SUPPLIER_PDF)

        