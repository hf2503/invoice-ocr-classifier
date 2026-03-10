import streamlit as st
import pandas as pd
import os
import time
import csv
from src import config
from src.batch_invoice_preprocessing import batch_invoice_preprocessing
from src.utils import clear_result_and_raw,clear_result_csv


# ----------------- Page -----------------
st.set_page_config(page_title="Invoice Classifier",
                   layout="wide",
                   page_icon='📄 Invoice Classifier',
                   initial_sidebar_state="collapsed"
                   )
st.title(f"📄 INVOICE CLASSIFIER")
st.caption("Semi-automatic recognition + accounting validation")

#on s'assure de l'existence du dossier des inputs
os.makedirs(config.INPUT_DIR, exist_ok=True)

#on s'assure de l'existence du dossier du suivi
os.makedirs(config.SUIVI_DIR,exist_ok=True)

#variable pour avoir un set des fichier dèjà traité et éviter les doublons
os.makedirs(config.FACTURES_BRUTES_DIR, exist_ok=True)
already_archived = set(os.listdir(config.FACTURES_BRUTES_DIR))

#----initialisaton des csv----------

csv_a_initialiser = {
    config.RESULTAT_CSV : config.COLUMNS_SUIVI,
    config.SUIVI_CSV : config.COLUMNS_SUIVI,
    config.ARCHIVE_CSV : config.COLUMNS_SUIVI_BRUTE
}


    #on verifie si les dossiers contenant les resultats ,le suivi et les archives existent

for path, columns in csv_a_initialiser.items():
    os.makedirs(os.path.dirname(path),exist_ok=True)
    
    #on teste si le csv existe ou qu'il n'est pas vide

    try:
        with open(path,'a',newline='',encoding='utf-8') as f:
            writer = csv.writer(f,delimiter=';')
            if not os.path.exists(path) or os.path.getsize(path) == 0 : 
                writer.writerow(columns)


    except PermissionError:
        st.error(f"veuillez fermer le fichier excel suivant : {os.path.basename(path)}")


#key pour modifier l'état du widget traitement des factures pour vider le buffer de streamlit
#afin de pouvoir reseter

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def reset_uploader():
    #permet de changer l'etat de la session 
    st.session_state["uploader_key"] += 1




left,right = st.columns([1,2],gap ='large')


with left:
    
    st.subheader("Configuration")
    stamp_text = st.text_input(
        "Validation Stamp",
        value= "", #valeur par défaut
        placeholder="verified on",
        help = "text used to validate that the document is an invoice"
    )
    
    stamp_text = stamp_text.strip() or "verified on"

    # st.sidebar.radio('write your company stamp')

    
    st.subheader("Importer des PDF")
    uploaded_files = st.file_uploader("Drop your invoice PDFs:",
                                      type="pdf",
                                      accept_multiple_files=True,
                                      key=f"uploader_{st.session_state['uploader_key']}")
    if uploaded_files:

        for files in uploaded_files:
            

            filename = os.path.basename(files.name or "upload.pdf")

            #on vérifie que le file n'a pas été dèja traité
            if filename in already_archived:
                st.warning(f" ⚠️ The file {filename} has already been processed")
                continue

            save_path = os.path.join(config.INPUT_DIR,filename) 
            with open(save_path,'wb') as f:
                f.write(files.getbuffer())
        st.success(f"{len(uploaded_files)} PDF file(s) added to folder {config.INPUT_DIR}")

    else :
        st.info("No files to process")
        st.stop()

    st.divider()
    c1,c2 = st.columns(2)
    process_clicked = c1.button(":shark: Traiter",type = "primary",use_container_width=True)
    clear_clicked = c2.button("\U0001F528 Clear",type ="secondary",use_container_width=True)

    if process_clicked:

        #on controle les fichiers csv ne sont pas ouverts
        check_csv_closed = list(csv_a_initialiser.keys())

        csv_error= []
        
        # st.write(f"🔍 Vérif CSV à contrôler : {check_csv_closed}")

        for csv_path in check_csv_closed:

            try:
                with open(csv_path,'a') as file:
                    # os.rename(csv_path,csv_path) # on essaye de renommer le fichier (avec le meme nom) pour s'assurer s'il est verrouillé ou non
                    pass
            except PermissionError :
                csv_error.append(os.path.basename(csv_path))

            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
                st.stop()
            
        if csv_error:
            #-------------debug---------------------
            st.write(f"les erreurs sont {csv_error}")
            st.error(f"⚠️ Processing cannot start because the following file(s) are open in Excel: {''.join(csv_error)}.\n\n"
                     "Please close them and try again.")
            
        #     Bouton pour retester sans recharger la page
            if st.button("🔁 Retry"):
                st.rerun()

        else:

            with st.spinner(text="\U000023F0 Processing in progress",
                            show_time=True,
                            width="content"):

                batch_invoice_preprocessing(config.INPUT_DIR,
                                            key_word=stamp_text)
                st.toast("Processing completed",icon="😍")
                st.balloons()
                # reset_uploader()
    
    if clear_clicked:
        with st.spinner(text=" 🫧Cleaning"):
            #clear_result_and_raw(config.OUTPUT_DIR)
            clear_result_csv(config.OUTPUT_DIR)
            clear_result_and_raw(config.INPUT_DIR)
            st.balloons()
        st.toast("Uploaded PDFs removed", icon="😄")
        reset_uploader()
        st.rerun()
    
    with right:
        st.subheader("Resultats")
        resultat_csv = config.RESULTAT_CSV
        
        if os.path.exists(resultat_csv) and os.path.getsize(resultat_csv):
            
            df = pd.read_csv(resultat_csv,sep=';')
            st.info(f"{df.shape[0]} invoices processed")
            st.dataframe(df)
        
        else:
            df = None
            st.info("No results available")
    
    with st.expander(":point_right: Help / User Guide"):
        st.subheader("Information & Paths")
        st.write(f" Input folder : {config.INPUT_DIR}")
        st.write(f" Output folder : {config.OUTPUT_DIR}")
        st.write(f" Results summary table : {config.RESULTAT_CSV}")
        st.info("Tip: use the **Upload** section to add PDFs, then click **Process**.\n"
                "The **Clear** button resets everything.")
        st.info(f"The Excel files {','.join([config.ARCHIVE_CSV,config.SUIVI_CSV,config.RESULTAT_CSV])} must be closed before starting the processing.")





