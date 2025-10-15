import streamlit as st
import pandas as pd
import os

from src import config
from src.batch_invoice_preprocessing import batch_invoice_preprocessing
from src.utils import clear_result

st.set_page_config(page_title="Classifieur de factures", layout="wide")
st.title("classifieur de factures")


# -------------Upload-------------------#

uploaded_files = st.file_uploader("Déposez vos factures PDF:",type='pdf')

if uploaded_files:
    filename = os.path.basename(uploaded_files.name or "upload.pdf")
    save_path = os.path.join(config.INPUT_DIR,filename) 
    with open(save_path,'wb') as f:
        f.write(uploaded_files.getbuffer())
    st.success(f"{uploaded_files} fichier pdf ont été ajoutées au dossier {config.INPUT_DIR}")

#---------run processing------------------#

if st.button("traitement des factures", type="primary") :
    st.spinner(text='En cours de traitement',show_time=True)
    batch_invoice_preprocessing(config.INPUT_DIR)
    st.success("traitement terminé")

#---------results------------------------#

# invoice_csv = os.path.join(config.OUTPUT_DIR,"train_data.csv")

invoice_csv = config.RESULTAT_CSV

if os.path.exists(invoice_csv):
    df = pd.read_csv(invoice_csv,sep=';')
    st.subheader("resultat")
    st.dataframe(df)

else:
    st.info("resultats non disponibles")

if st.button("effacer les résultats", type="primary"):
    st.spinner(text='en cours de suppression', show_time=True)
    clear_result(config.OUTPUT_DIR)
