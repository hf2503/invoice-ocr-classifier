# Automated Invoice OCR & Filing System

## Project Overview

This project implements an automated invoice processing system designed to extract,classify and file scanned pdf invoices
in a structured and traceable way.

It combines OCR (Tesseract), image preprocessing (OpenCV) , and rule-based matching to detect companies, suppliers, and VAT numbers
from invoice documents.

This system is built to support the batch processing, the file structured and full traceability through csv tracking and logging.



## Table of Contents
 
1. Introduction  
2. Installation  
3. Architecture  
4. Folder Description  
5. How to Use  
6. Conclusion and Future Improvements  






## 1.  Introduction

Sometimes in accounting workflows, PDF file can contain numerous invoices merged and scanned in a random order. These files mix lot of different information like company, supplier...

Manually splitting, indentifying, and filing such invoices is time consuming,  error-prone and difficult to track at scale.

The project addresses this problem by automatically analysing each pdf , detecting one-page invoice (and two-pages-invoice) and classifying them in the appropriate company and supplier directories

For each invoice, the system :

  -  Extract text from the PDF's file scanned
  -  Identifies the target subsidiary of the receiving organisation and the supplier
  -  Validates that the page is an invoice by detecting the validation internal stamp configurable in the system settings
  -  handler invoices-two-page
  -  Saved the processed invoiced in the appropriate directory
  - Archive the raw/original pdf
  - Save traceability information in csv files

## 2. Installation

### 2.1 Clone the repository

```bash
git clone https://github.com/invoice_classifier/classifier.git
cd classifier
```

### 2. Run docker-compose:

```bash
docker-compose up -d --build
```

## 3. Architecture

### 3.1 Project structure
```

LUX_INVOICE_2/
│
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
│
├── data/
│   ├── raw_invoices_to_process/    # Incoming raw PDFs
│   ├── company_list.csv            # Company registry reference
│   └── supplier_list.csv           # Supplier registry reference
│
├── logs/
│   └── invoice_processing.log      # Application logs
│
├── script/
│   └── Lancer_LuxInvoice.bat       # Windows launcher
│
├── src/
│   ├── __init__.py
│   ├── batch_invoice_preprocessing.py  # Batch ingestion pipeline
│   ├── process_invoice_pdf.py          # OCR + classification engine
│   ├── config.py                       # Configuration & constants
│   ├── main.py                         # Application entry logic
│   └── utils.py                        # Helper functions
│
├── app.py                          # Streamlit application entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements_docker.txt
└── README.md


```

### 3.2 Architecture Diagram

```mermaid
flowchart TD

    A[Input folder raw invoices to process]
    B[Batch ingestion]
    C[Invoice processing]
    D[Convert pdf to png pages]
    E[OCR and page analysis]
    F[Detect and merge multi page invoices]
    G[Validate invoice stamp]
    H[Resolve company and supplier paths]
    I[Save classified invoice pdf]

    AR[Archive raw pdf and archive csv]
    LG[Write logs]
    PG[Store png pages for audit]
    RS[Write results csv]
    TR[Write tracking csv]

    A --> B --> C --> D --> E --> F --> G --> H --> I

    B --> AR
    C --> LG
    D --> PG
    I --> RS
    I --> TR

```
## 4.  Folder Description

### 4.1 raw_invoices_to_process/

  - Contains raw pdf files to be processesd
  - Each file contain multiple mixed invoice
  - After successful processing, files are moved to the archive folder archived_raw_invoices/raw_invoices/,ensuring that it will not be processed again

  ##### raw_invoices/
  The main purpose of this folder is to track processed file and ensured that files are not preprocessed twice

  Archive of processed raw PDFs
    - Store the original PDF before preprocessing

  #### Tracking file
  
  **Archive_raw_invoices.csv** :
    
  colummns : 
    - raw_invoice
    - date
    - check-in time
    - sha1_pdf

this file ensures traceability of incoming documents

### 4.2 classified_invoices/

This folder contains the filed PDF invoices , results of the pipeline .

Invoices are saved on the following path (2 configurations) : 

```
  - company/supplier/invoice_time_stamp.pdf
  - parent_company/company/supplier/invoice_timestamp.pdf

```

  #### Session summary file

  results.csv 

  columns : 
  - invoice_processed
  - parent_company
  - company_name
  - supplier_name
  - date
  - sha1_pdf
    
  This file is used for result verification and control at the end of the session

### 4.3 tracking/

This folder contains files and folder for tracking and checking results

  #### Processed_invoice_archive/
  This folder contains all the invoice's page in PNG format . For exemple 50 pages PDF generates 50 PNG files.
  In addition it allows manual verification by accounting staff

  #### Processed_invoices_tracking.csv
  
  columns : 
  - invoice_processed
  - parent_company
  - company_name
  - supplier_name
  - date
  - sha1_pdf

 ### 4.4 Reference and mapping table 

 The systeme relies on two CSV mapping table

  company_list.csv
  columns : 
  - company_name_invoice (company name in the invoice)
  - company_name_registery (folder name)
  - ID_TVA
  - parent_company

  supplier_list.csv
  columns : 
  - supplier_invoice (supplier name on the invoice)
  - supplier registery (folder name)
  - TVA

 These files contain reference data used to match OCR-extracted text with the name of the company (company_name_invoice) . The system searches for a match with the VAT number or the company name or supplier name 
 written on the invoice.

## 5. HOW TO USE

### 5.1 Launch the application and start the application with docker
```
git clone https://https://github.com/hf2503/invoice-ocr-classifier.git
cd invoice-ocr-classifier
docker compose up --build
```
Once the container is running, open your browser and go to  http://localhost:8501

![Alt text](screenshot/image_1.png)


This will display the streamlit interface of the invoice Classifier application

The main page allows users to configure the validation settings and upload invoie documents for processing.

The validation stamp field defines the internal accounting validation stamp used to confirm that a pahe coressponds to a valid invoice

Once uploaded, the files will be prepared for processing by the OCR pipeline

### 5.2 Upload Invoice Documents

![Alt text](screenshot/image_2.png)

Once the application is open, users can upload invoice documents using the drag-and-drop area or by clicking the browse files button.

A confirmation message appears to indicate that the file has been successfully added to the processing folder

At the stage, the file is ready to be analyzed by the OCR pipeline. To start the invoice analysis,click the button Process


Once the processing pipeline is complete, the application display's a summary of the results in the Results section of the interface.

All classufued invoices are stored in the following folder:

```
classified_invoices

```


## Conclusion and future improvements:

Possible improvements

Several enhancements could further improve the system:

Machine learning based classification
Replace or complement rule-based matching with machine learning models to improve supplier and company detection.

Automatic invoice number detection
Extract invoice numbers and other key metadata to enrich traceability.

Better OCR accuracy
Integrate additional preprocessing techniques or advanced OCR models to improve recognition on low-quality scans.

Real-time CSV reloading
Allow the application to automatically reload reference tables (company_list.csv, supplier_list.csv) without restarting the container.

API integration
Expose the processing pipeline as a REST API to integrate the system with accounting software or document management systems.

User interface improvements
Add more visual feedback during processing and allow manual correction of classification results.

These improvements would make the system more robust and suitable for larger-scale document processing environments.


















