
FROM python:3.11-slim-bookworm

#dossier de travail
WORKDIR /app

#on se met en root pour installer les dependances
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-fra \
    poppler-utils \
    libgl1 \
    libglib2.0-0\
    && rm -rf /var/lib/apt/lists/*

#copy du requirement.txt
COPY requirements_docker.txt /app/requirements_docker.txt

#installation des dépendances python
RUN pip install --no-cache-dir -r requirements_docker.txt

#copie du projet dans app
COPY . /app

#variable d'environnement
ENV PYTHONPATH=/app
ENV TESSERACT_PATH=/usr/bin/tesseract
# ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

#port streamlit
EXPOSE 8501

#commande de demarrage
CMD ["streamlit","run","app.py","--server.port=8501","--server.address=0.0.0.0"]
