import subprocess

subprocess.run("rm -rf ../data/classified_invoices/*",shell=True)
subprocess.run("rm -rf ../data/tracking/*",shell=True)
subprocess.run("rm -rf ../data/archived_raw_invoices/*",shell=True)