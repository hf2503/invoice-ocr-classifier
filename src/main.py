
import pytesseract
from datetime import datetime
import matplotlib.pyplot as plt
import os
from config import *
from utils import *
import traceback



pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def convert_invoice_pdf(input_pdf:str,
                        company_csv = company_df,
                        company_invoice=LIST_COMPANY_NAME_INVOICE,
                        company_directory=LIST_COMPANY_NAME_DIRECTORY,
                        company_tva = LIST_COMPANY_TVA,
                        output_dir=OUTPUT_DIR,
                        supplier=LIST_SUPPLIER,
                        tva_supplier_list=LIST_TVA_SUPPLIER,
                        NEW_SUPPLIER=NEW_SUPPLIER,
                        ):
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

            #company detection
            company_name = check_company(text,
                                         company_list_name_invoice=company_invoice,
                                         company_list_tva=company_tva
                                         )
            
            print(f'coucou {company_name}')

            if not company_name == 'new_company':
                directory_company = company_csv.loc[company_csv['company_name_invoice'] == company_name,'company_name_registery'].values[0]
                print(directory_company)
                directory_company_path = make_directory_company(output_dir,directory_company)
                print(directory_company_path)
            
            else:
                directory_company = 'new_company'
                directory_company_path = make_directory_company(output_dir,directory_company)
                print(directory_company_path)


            #supplier detection
            supplier_name = check_supplier(text,supplier_list=supplier,tva_supplier_list=tva_supplier_list)

            if supplier_name:
                norm_name = normalise_supply_name(text = supplier_name)

            else:
                norm_name = normalise_supply_name(text = NEW_SUPPLIER)
            
            dir_path_supply = make_directory_supply(directory_company=directory_company_path,directory_supplier=norm_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image.convert('RGB').save(os.path.join(dir_path_supply,f"facture{timestamp}.pdf"))


            # dir_path = make_directory_supply(output_dir=output_dir,directory=norm_name)
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # image.convert('RGB').save(os.path.join(dir_path,f"facture{timestamp}.pdf"))
            # print(f"facture{i+1}.pdf enregistré dans {dir_path}")

        
        else:
            print("Factures non validées")


def reclassify_from_the_directory_new_company(input_new:str,
                                              new_company_list=LIST_NEW_SUPPLIER,
                                              tva_new_supplier_list=LIST_TVA_NEW_SUPPLIER,
                                              new_supplier=NEW_SUPPLIER):
    """reclassify the invoice in the director
    when the csv LIST_SUPPLIER is update

    Raises:
        TypeError: _description_
    """
    print('hello')
    print(os.listdir(input_new))
    if os.listdir(input_new):
        for directory in os.listdir(input_new):
            # print(f'directory:{directory}')
            # print(f'new_supplier:{new_supplier}')
            path_directory_supply = os.path.join(input_new,directory)
            # print(f'path_directory_supply: {path_directory_supply}')
            for new_s in os.listdir(path_directory_supply):
                # print(f'proof:{os.listdir(path_directory_supply)}')
                if new_s ==  new_supplier:
                    # print(f'directory:{new_s}')
                    path_directory = os.path.join(path_directory_supply,new_s)
                    # print(f'path_supply : {path_directory}')
                    # print(f'list_supply: {os.listdir(path_directory)}')
                    for supplier in os.listdir(path_directory):
                        print(f'list_supplier_pdf:{os.listdir(path_directory)}')
                        new_path = os.path.join(path_directory,supplier)
                        image = convert_pdf_to_PIL(new_path)
                        print(new_path)
                        try:
                            new_text = pytesseract.image_to_string(image[0])
                        except Exception as e:
                            print(f"on eu l'erreur suivante avec l'OCR pytesseract sur le {filename} : {e}")
                        # print(new_text)  
                        new_supply = check_supplier(new_text,new_company_list,tva_new_supplier_list)
                        print(new_supply)
                        if new_supply:
                            norm_new_text = normalise_supply_name(new_supply)
                            #à modifier pour envoyer le supply detecter dans le bon dossier
                            dir_new_path = make_directory_company(path_directory_supply,norm_new_text)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            # print(image)
                            image[0].convert('RGB').save(os.path.join(dir_new_path,f"facture_{timestamp}.pdf"))
                
                        #delete the pdf file
                            os.remove(new_path)
                            print(f"suppression du fichier {new_path}")
            
            else :
                print('1')
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
                traceback.print_exc()
        else:
            raise TypeError(f"le fichier {filename} doit être au format pdf")
        
    reclassify_from_the_directory_new_company(input_new = OUTPUT_DIR)

        