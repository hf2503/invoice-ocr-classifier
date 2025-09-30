import subprocess

subprocess.run("rm -rf ../data/factures/*",shell=True)
subprocess.run("rm -rf ../data/train/*",shell=True)
subprocess.run("rm -rf ../train_final/dataset/*",shell=True)