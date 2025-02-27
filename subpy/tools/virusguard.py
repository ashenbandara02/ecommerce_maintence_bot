import pandas as pd
import hashlib
import zipfile
import sys
import os

current_directory = str(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(current_directory)

def virus_scan(file_path):
    if not os.path.exists(file_path):
        return "X"
    
    if not file_path.endswith('.zip'):
        return "X"

    df = pd.read_csv("/home/ProjectExcel/subpy/tools/malware_hashes.csv", usecols=[1], header=None)
    known_malicious_hashesx = [x.strip('"') for x in df[1].astype(str)]
    known_malicious_hashes = [x.strip(' "').strip() for x in known_malicious_hashesx]

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                with zip_ref.open(file) as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    print(f"Scanning for virus in Hash : {file_hash}")
                    if file_hash in known_malicious_hashes:
                        return True
    except Exception as e:
        return "PasswordProtected"
    
    return False

