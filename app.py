import streamlit as st
import pandas as pd
import os

from src import config
from src.batch_invoice_preprocessing import batch_invoice_preprocessing
from src.utils import clear_result_and_raw


# ----------------- Page -----------------
st.set_page_config(page_title="Classifieur de factures",
                   layout="wide",
                   page_icon=':grinning:',
                   initial_sidebar_state="collapsed"
                   )
st.title(f"{':grinning:'} CLASSIFIEUR DE FACTURES")
st.caption("Reconnaissance semi-automatique + correction comptable")



#key pour modifier l'état du widget traitement des factures pour vider le buffer de streamlit

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def reset_uploader():
    #permet de changer l'etat de la session 
    st.session_state["uploader_key"] += 1


tab_upload, tab_results, tab_about = st.tabs(["importer","Resultats","Infos"])


with tab_upload:
    st.subheader("Importer des PDF")
    uploaded_files = st.file_uploader("Déposez vos factures PDF:",
                                      type="pdf",
                                      accept_multiple_files=True,
                                      key=f"uploader_{st.session_state['uploader_key']}")
    if uploaded_files:

        for files in uploaded_files:
            filename = os.path.basename(files.name or "upload.pdf")
            save_path = os.path.join(config.INPUT_DIR,filename) 
            with open(save_path,'wb') as f:
                f.write(files.getbuffer())
        st.success(f"{len(uploaded_files)} fichier(s) pdf ont été ajoutée(s) au dossier {config.INPUT_DIR}")

    else :
        st.info("il y aucun fichier à traiter")

    st.divider()
    c1,c2,c3 = st.columns([1,1,6])
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
            clear_result_and_raw(config.OUTPUT_DIR)
            clear_result_and_raw(config.INPUT_DIR)
            st.balloons()
        st.toast("résultats effacés", icon="😄")
        reset_uploader()
        st.rerun()
    
    with tab_results:
        st.subheader("Resultats")
        resultat_csv = config.RESULTAT_CSV
        
        if os.path.exists(resultat_csv):
            df = pd.read_csv(resultat_csv,sep=';')
            st.info(f"{df.shape[0]} factures ont été traitées")
            st.dataframe(df)
        
        else:
            df = None
            st.info("il n'y a pas de resultats")
    
    with tab_about:
        st.subheader("info & chemins")
        st.write(f" Dossier d'entrée : {config.INPUT_DIR}")
        st.write(f" Dosiiser de sorie : {config.OUTPUT_DIR}")
        st.write(f" Tableaux recap des résultats : {config.RESULTAT_CSV}")
        st.info("Astuce : utilisez l'onglet ** importer ** pour ajouter des pdf , puis **traiter**."
                "le bouton **Effacer** remets tout à zéro")






# # -------------Upload-------------------#
# #avec modification de la key du widget pour pouvoir le reinitialiser

# uploaded_files = st.file_uploader("Déposez vos factures PDF:",
#                                   type="pdf",
#                                   accept_multiple_files=True,
#                                   key=f"uploader_{st.session_state['uploader_key']}")



# if uploaded_files:

#     for files in uploaded_files:
#         filename = os.path.basename(files.name or "upload.pdf")
#         save_path = os.path.join(config.INPUT_DIR,filename) 
#         with open(save_path,'wb') as f:
#             f.write(files.getbuffer())

#     st.success(f"{len(uploaded_files)} fichier pdf ont été ajoutées au dossier {config.INPUT_DIR}")

# else :
#     st.info("il y aucun fichier à traiter")

# #---------run processing------------------#

# if st.button("traitement des factures", type="primary") :
#     with st.spinner(text='En cours de traitement ...',show_time=True):
#         batch_invoice_preprocessing(config.INPUT_DIR)
#     st.balloons()
#     st.success("traitement terminé")

#     #------------reset de l'uploader ----------------
#     reset_uploader()
#     # st.rerun()

# #---------results------------------------#

# resultat_csv = config.RESULTAT_CSV

# st.subheader("Résultats")

# if os.path.exists(resultat_csv):
#     df = pd.read_csv(resultat_csv,sep=';')
#     st.info(f"{df.shape[0]} factures ont été traitées")
#     st.dataframe(df)

# else:
#     st.info("resultats non disponibles")

# if st.button("effacer les résultats", type="primary"):
#     with st.spinner(text='en cours de suppression', show_time=True):
#         clear_result_and_raw(config.OUTPUT_DIR)
#         clear_result_and_raw(config.INPUT_DIR)
#         st.balloons()
#     st.info("résultats effacés")
#     st.rerun()

# #------------Raffraichissement de l'interface utilisateur ----------


