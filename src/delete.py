import subprocess
import shutil

# subprocess.run("rm -rf ../data/classified_invoices/*",shell=True)
# subprocess.run("rm -rf ../data/tracking/*",shell=True)
# subprocess.run("rm -rf ../data/archived_raw_invoices/*",shell=True)

# data_path = r'C:\Users\User\Documents\LUX_INVOICE_2\data'

shutil.rmtree(r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\archived_raw_invoices', ignore_errors=True)
shutil.rmtree(r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\classified_invoices',ignore_errors=True)
shutil.rmtree(r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\tracking',ignore_errors=True)

# shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPESA FRS 03 11 25 copy.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')

# shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\spt frs 13 06 25.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')

# shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPESA FRS 14 11 25.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')

# shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPPO FRS 03 11 25.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')

# shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPT\SPT_frs_01-0625\FRS SPT 23 05 2025.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')

# shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPT\SPT_frs_01-0625\spt 30 04 2025.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')


shutil.copy(r"C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPT\SPT_frs_01-0625\SPT_FRS_20250116.pdf",r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')