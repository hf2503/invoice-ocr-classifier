import subprocess

subprocess.run("rm -rf ../data/factures/*",shell=True)
subprocess.run("rm -rf ../data/suivi/*",shell=True)
subprocess.run("rm -rf ../data/facture_brutes_archivees/*",shell=True)