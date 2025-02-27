import requests
import zipfile
import time
import sys
import os


current_directory = str(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(current_directory)

from virusguard import virus_scan



def get_file_size_in_mb(file_path):
    # file_path = full path
    try:
        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        return int(round(file_size_mb))
    except:
        return None
    

def get_unzipped_size_mb(zip_path):
    total_size = 0
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                total_size += file_info.file_size
        return str(round((total_size / 1048576), 2))
    except:
        return 0

def count_files_and_folders_in_zip(zip_file_path):
    file_count = 0
    folder_count = 0
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    folder_count += 1
                else:
                    file_count += 1
            return str(file_count+folder_count)
    except zipfile.BadZipFile as e:
        return "X"
    except FileNotFoundError as e:
        return "X"



def report_retrieve(resource, filename):
    url = 'https://www.virustotal.com/vtapi/v2/file/report'
    params = {'apikey': '4720a4ebcf81a9d4fbb363e7225c0db87e1e78505784aeceea7e966bc3198efd', 'resource': str(resource)}

    loop = 0
    while loop <= 3:
        proceed2 = True     
        try:
            response_get = requests.get(url, params=params)
        except: 
            proceed2 == False

        if proceed2:
            if response_get.status_code == 200:
                print(f"[ \u2713 ] Getting Virus Report try {str(loop+1)} !")
                
                get_data = response_get.json()
                proceed3 = True
                try:
                    viruses = get_data['positives']
                    # total = get_data['total']
                except Exception as e:
                    proceed3 = False
                    with open("virusesanderrors.txt", "a", encoding="utf-8") as ve:
                        ve.write(f"Error with getting viruses: {e}\n")
                    # return ["X", 0]

                if proceed3:
                    if viruses == 0:
                        return [count_files_and_folders_in_zip(filename), get_unzipped_size_mb(filename)]
                    else:
                        with open("virusesanderrors.txt", "a", encoding="utf-8") as ve:
                            ve.write("Viruses present \n")
                        return ["Virus", 0]
                else:
                    time.sleep(60)
            else:
                time.sleep(60)
        loop += 1
    
    return ["X", 0]
        
                


def report_scan_activate(filename):
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'

    params = {'apikey': '4720a4ebcf81a9d4fbb363e7225c0db87e1e78505784aeceea7e966bc3198efd'}

    response = requests.get(url, params=params)

    files = {'file': (filename, open(filename, 'rb'))}

    if get_file_size_in_mb(filename) > 31:
        if virus_scan(filename) == True:
            return ["Virus", 0]
        elif virus_scan(filename) == False:
            return [count_files_and_folders_in_zip(filename), get_unzipped_size_mb(filename)]
        elif virus_scan(filename) == "PasswordProtected":
            return False
        else:
            return ["X", 0]


    proceed1 = True
    try:
        response = requests.post(url, files=files, params=params)
    except Exception as e:
        proceed1 = False
        with open("virusesanderrors.txt", "a", encoding="utf-8") as ve:
            ve.write(f"Posting Error : {e}\n")
        return ["X", 0]

    if proceed1:
        if response.status_code == 200:
            print("[ \u2713 ] Virus Report Requested")
            post_return_data = response.json()
            resource = post_return_data['resource']
            if len(resource) > 20:
                # time.sleep(300)
                return report_retrieve(resource, filename)
            else:
                with open("virusesanderrors.txt", "a", encoding="utf-8") as ve:
                    ve.write(f"Didnt Get a Resource \n")
                return ["X", 0]
        else:
            with open("virusesanderrors.txt", "a", encoding="utf-8") as ve:
                ve.write(f"Error with posting status code \n")
            return ["X", 0]