import subprocess

subprocess.run("rm -rf ../data/factures_classees/*",shell=True)
subprocess.run("rm -rf ../data/suivi/*",shell=True)
subprocess.run("rm -rf ../data/factures_brutes_archivees/*",shell=True)