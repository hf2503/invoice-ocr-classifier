# Automated Invoice OCR & Filing System

## Project Overview

This project implements an automated invoice processing system designed to extract,classify and file scanned pdf invoices
in a strucutured and traceable way.

It combines OCR (Tesseract), image preprocessing (OpenCV) , and rule-based matching to detect companies, suppliers, and VAT numbers
from invoice documents.

This system is built to support the batch processing, the file structured and full traceability, through csv tracking and logging

## Table of contents

## Introduction

Sometimes in accounting workflows, pdf's file can contain numerous invoices merged and scanned in a random order. This files mix lot of different information like company, supplier...

Manually splitting, indentifying, and filing such invoices is time consuming,  error-prone and difficult to track at scale.

The project addresses this problem by automatically analysing each pdf , detecting one-page invoice (and two-pages-invoice) and classifying them in the appropriate company and supplier directories

For each invoice, the system :

  - 


