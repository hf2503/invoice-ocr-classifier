#official Airflow image with python 3.11
FROM apache/airflow:2.8.2-python3.11

#working directory inside the container
WORKDIR /opt/airflow

#copy source code and DAGS
COPY ./src /opt/airflow/src
COPY ./dags /opt/airflow/dags
COPY requirements.txt .

#install python dependencies
RUN pip install -r requirements.txt

#Become root to install OS-level dependencies
USER root

RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils && apt-get clean

#return to airflow user
USER airflow