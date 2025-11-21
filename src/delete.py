import subprocess
import shutil

# subprocess.run("rm -rf ../data/classified_invoices/*",shell=True)
# subprocess.run("rm -rf ../data/tracking/*",shell=True)
# subprocess.run("rm -rf ../data/archived_raw_invoices/*",shell=True)

# data_path = r'C:\Users\User\Documents\LUX_INVOICE_2\data'

shutil.rmtree(r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\archived_raw_invoices', ignore_errors=True)
shutil.rmtree(r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\classified_invoices',ignore_errors=True)
shutil.rmtree(r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\tracking',ignore_errors=True)

shutil.copy(r'C:\Users\Windows\Documents\LUX_INVOICE_2\invoice_issue\SPAM\SPAM FRS 16 09 2025.pdf',r'C:\Users\Windows\Documents\LUX_INVOICE_2\data\raw_invoices_to_process')