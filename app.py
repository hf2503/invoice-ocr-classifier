import streamlit as st
import pandas as pd
import os

from src import config
from src.batch_invoice_preprocessing import batch_invoice_preprocessing

st.set_page_config(page_title="Classifieur de factures", layout="wide")
st.title("classifieur de factures")


# -------------Upload-------------------#

uploaded_files = st.file_uploader("Déposez vos factures PDF:",type='pdf')

if uploaded_files:
    for file in uploaded_files:
        save_path = os.path.join(config.INPUT_PDF_FOLDER,file.decode())
        with open(save_path,'wb') as f:
            f.write(file.getbuffer())
    st.success(f"{len(uploaded_files)} fichier pdf ont été ajoutées au dossier {config.INPUT_PDF_FOLDER}")

#---------run processing------------------#

if st.button("traitement des factures", type="primary") :
    st.spinner(text='En cours de traitement',show_time=True)
    batch_invoice_preprocessing(config.INPUT_PDF_FOLDER)
    st.success("traitement terminé")

#---------results------------------------#

invoice_csv = os.path.join(config.TRAIN_DIR,"train_data.csv")

if os.path.exists(invoice_csv):
    df = pd.read_csv(invoice_csv)
    st.subheader("resultat")
    st.dataframe(df)

else:
    st.info("resultats non disponibles")