import streamlit as st
import pandas as pd
import os

from src import config
from src.batch_invoice_preprocessing import batch_invoice_preprocessing
from src.utils import clear_result_and_raw,clear_result_csv


# ----------------- Page -----------------
st.set_page_config(page_title="Classifieur de factures",
                   layout="wide",
                   page_icon=':grinning:',
                   initial_sidebar_state="collapsed"
                   )
st.title(f"{':grinning:'} CLASSIFIEUR DE FACTURES")
st.caption("Reconnaissance semi-automatique + correction comptable")

#on s'assure de l'existence du dossier des inputs
os.makedirs(config.INPUT_DIR, exist_ok=True)


#variable pour avoir un set des fichier dèjà traité et éviter les doublons
os.makedirs(config.FACTURES_BRUTES_DIR, exist_ok=True)
already_archived = set(os.listdir(config.FACTURES_BRUTES_DIR))

#key pour modifier l'état du widget traitement des factures pour vider le buffer de streamlit

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def reset_uploader():
    #permet de changer l'etat de la session 
    st.session_state["uploader_key"] += 1


left,right = st.columns([1,2],gap ='large')


with left:
    st.subheader("Importer des PDF")
    uploaded_files = st.file_uploader("Déposez vos factures PDF:",
                                      type="pdf",
                                      accept_multiple_files=True,
                                      key=f"uploader_{st.session_state['uploader_key']}")
    if uploaded_files:

        for files in uploaded_files:

            filename = os.path.basename(files.name or "upload.pdf")

            #on vérifie que le file n'a pas été dèja traité
            if filename in already_archived:
                st.warning(f" ⚠️ le fichier {filename} a déja été traité")
                continue

            save_path = os.path.join(config.INPUT_DIR,filename) 
            with open(save_path,'wb') as f:
                f.write(files.getbuffer())
        st.success(f"{len(uploaded_files)} fichier(s) pdf ont été ajoutée(s) au dossier {config.INPUT_DIR}")

    else :
        st.info("il y aucun fichier à traiter")

    st.divider()
    c1,c2 = st.columns(2)
    process_clicked = c1.button(":shark: Traiter",type = "primary",use_container_width=True)
    clear_clicked = c2.button("\U0001F528 Effacer",type ="secondary",use_container_width=True)

    if process_clicked:
        with st.spinner(text="\U000023F0 en cours de traitement"):

            batch_invoice_preprocessing(config.INPUT_DIR)
            st.toast("Traitement terminé",icon="😍")
            st.balloons()
            # reset_uploader()
    
    if clear_clicked:
        with st.spinner(text=" 🫧nettoyage"):
            #clear_result_and_raw(config.OUTPUT_DIR)
            clear_result_csv(config.OUTPUT_DIR)
            clear_result_and_raw(config.INPUT_DIR)
            st.balloons()
        st.toast("pdf importés effacés", icon="😄")
        reset_uploader()
        st.rerun()
    
    with right:
        st.subheader("Resultats")
        resultat_csv = config.RESULTAT_CSV
        
        if os.path.exists(resultat_csv):
            df = pd.read_csv(resultat_csv,sep=';')
            st.info(f"{df.shape[0]} factures ont été traitées")
            st.dataframe(df)
        
        else:
            df = None
            st.info("il n'y a pas de resultats")
    
    with st.expander(":point_right: Aide/Guide d'utlisation"):
        st.subheader("info & chemins")
        st.write(f" Dossier d'entrée : {config.INPUT_DIR}")
        st.write(f" Dossier de sortie : {config.OUTPUT_DIR}")
        st.write(f" Tableaux recap des résultats : {config.RESULTAT_CSV}")
        st.info("Astuce : utilisez l'onglet ** importer ** pour ajouter des pdf , puis **traiter**."
                "le bouton **Effacer** remets tout à zéro")





