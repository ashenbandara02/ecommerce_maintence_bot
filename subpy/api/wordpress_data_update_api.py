import os
import random
import re
import string
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# from wordpress_logger import login_to_wordpress
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloudflareapi import upload_static_action, delete_file, check_if_file_exists


# main_path = 'F:/work/projectexcel/'
main_path = '/home/ProjectExcel/updater_products/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def new_title_creator(a_title, version):
    version_pattern = r'\s+v\d+(\S+)?$'
    title_without_version = re.sub(version_pattern, '', a_title)

    return title_without_version.strip() + " v" + version

def remove_special_characters(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\,<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "")

def remove_special_characters2(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\,<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace(".", "")

def remove_special_characters3(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\,<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "-")

def remove_special_characters4(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\,<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "-").replace(".", "").replace("#", "").replace("!", "")

def remove_special_characters5(input_string):
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\<>?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace("–","-").replace("&", "-").replace(".", "").replace("#", "").replace("!", "").replace(",", "-")

def update_product(product_id, new_version, new_p_last_update, product_file_path, virus_guard, cookies):
    """
    Does all Nessasary work in the perticular product page and updates and returns.
    virus_guard_value = 0 -> Virus scripts Value, 1 -> unCompressed File size

    True: Updation Complete
    False: Failed to Update
    """

    ################################### Visit Login & Add Cookie ###################################

    ##### Windows 
    # options_cd = Options()
    # # options_cd.add_argument('--headless')
    # driver = webdriver.Chrome(options=options_cd) # Initialize the webdriver
    # options_cd.add_argument(f"user-agent={headers['User-Agent']}")
    # driver.maximize_window()

    ##### Ubuntu 
    options_cd = Options()
    options_cd.add_argument('--headless')
    options_cd.add_argument('--no-sandbox')
    options_cd.add_argument('--disable-dev-shm-usage')
    

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_cd) # Initialize the webdriver
    except:
        print("Chrome Stuck on Cache.......... Restarting in 100s")
        time.sleep(100)
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_cd) # Initialize the webdriver
        except:
            driver.quit()
            return ["Cannot Start Chrome Driver", ""]
        
    options_cd.add_argument(f"user-agent={headers['User-Agent']}")
    driver.maximize_window()

    try:
        driver.get("https://wptoolmart.com/chamarawp/")
    except:
        driver.quit()
        return ["Error: Cannot Load Url https://wptoolmart.com/chamarawp/", ""]

    for key, value in cookies.items():
        driver.add_cookie({
            'name': key,
            'value': value,
            'domain': 'wptoolmart.com',  
            'path': '/',  
        })

    ################### Visit Edit Page of Product with Product_id ##############################
    try:
        driver.get(f"https://wptoolmart.com/wp-admin/post.php?post={product_id}&action=edit")
        driver.implicitly_wait(10)
    except:
        driver.quit()
        return [f"https://wptoolmart.com/wp-admin/post.php?post={product_id}&action=edit", "Product Visit Failed"]
    
    ########################## Integrate Auto Update ############################################

    # Check for Successful Login
    try:
        WebDriverWait(driver, 60).until(EC.visibility_of_any_elements_located((By.CLASS_NAME , "wp-heading-inline")))
    except:
        driver.quit()
        return "Cookie fail"

    # Add the New Title
    # error = []

    check_1 = 0
    while True:
        try:
            the_product_title = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "title")))
            driver.execute_script("arguments[0].scrollIntoView(true);", the_product_title)
            driver.execute_script("arguments[0].click();", the_product_title)

            title = new_title_creator(the_product_title.get_attribute("value"), new_version)
            
            the_product_title.clear()
            the_product_title.send_keys(title)
            print("> Title Renewed <")
            break
        except Exception as e:
            if check_1 == 2:
                driver.quit()
                return [f"Error Adding Title", str(e)]
            
            time.sleep(3)
            check_1 += 1

    # changes the version
    check_2 = 0
    while True:
        try:
            the_product_version = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product-version")))
            driver.execute_script("arguments[0].scrollIntoView(true);", the_product_version)
            driver.execute_script("arguments[0].click();", the_product_version)

            the_product_version.clear()
            the_product_version.send_keys(new_version)
            print("> Version Renewed <")
            break
        except Exception as e:
            if check_2 == 2:
                driver.quit()
                return [f"Error Adding Version", str(e)]
            
            time.sleep(3)
            check_2 += 1

    # changes the last update
    check_3 = 0
    while True:
        try:
            the_product_update = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product-last-updated")))
            driver.execute_script("arguments[0].scrollIntoView(true);", the_product_update)
            driver.execute_script("arguments[0].click();", the_product_update)

            the_product_update.clear()
            the_product_update.send_keys(new_p_last_update)
            print("> Last Update Renewed <")
            break
        except Exception as e:
            if check_3 == 2:
                return [f"Error Adding Last Update Date", str(e)]
            time.sleep(3)
            check_3 += 1

    # changes the virus_guard_section
    has_virus = False
    if virus_guard[0] != "X" and virus_guard[0] != "Virus":
        check_virus_section = 0
        while True:
            try:
                virus_total = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "virus-total")))
                driver.execute_script("arguments[0].scrollIntoView(true);", virus_total)
                driver.execute_script("arguments[0].click();", virus_total)

                virus_total.clear()
                virus_total.send_keys(virus_guard[0])


                uncompressed_size = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "uncompressed-size")))
                driver.execute_script("arguments[0].scrollIntoView(true);", uncompressed_size)
                driver.execute_script("arguments[0].click();", uncompressed_size)

                uncompressed_size.clear()
                uncompressed_size.send_keys(virus_guard[1])
                print("> Virus Details Attached <")
                break
            except Exception as e:
                if check_virus_section == 2:
                    break
                time.sleep(3)
                check_virus_section += 1

    elif virus_guard[0] == "Virus":
        try:
            virus_total = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "virus-total")))
            driver.execute_script("arguments[0].scrollIntoView(true);", virus_total)
            driver.execute_script("arguments[0].click();", virus_total)

            virus_total.clear()


            uncompressed_size = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "uncompressed-size")))
            driver.execute_script("arguments[0].scrollIntoView(true);", uncompressed_size)
            driver.execute_script("arguments[0].click();", uncompressed_size)

            uncompressed_size.clear()
        except:
            pass


        has_virus = True


    new_file_path = ""
    try:
        oldfilename = product_file_path.split("/")[-1]
        oldfilename_list = oldfilename.split(".")
        oldfilename, extension = oldfilename_list[0], oldfilename_list[1]
        random_key_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        newfilename = oldfilename+"-000"+str(product_id)+f"-{random_key_code}"+"."+extension

        os.rename(product_file_path, os.path.join(os.path.dirname(product_file_path), newfilename))
        new_file_path = main_path + newfilename
    except:
        driver.quit()
        return ["Error Creating New Product File Name", ""]

    ### Changing file part
    check_4 = 0
    while True:
        try:

            file_download_url_change_check = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "file_url"))).find_element(By.CLASS_NAME, "input_text") 
            driver.execute_script("arguments[0].scrollIntoView(true);", file_download_url_change_check)
            driver.execute_script("arguments[0].click;", file_download_url_change_check)
            file_link = file_download_url_change_check.get_attribute("value")

            # check if it belongs to pub
            # upload_static_action, delete_file, check_if_file_exists
            link = ""
            if "storage.wptoolmart" in file_link:
                file_name = file_link.split("/")[-1]
                # check if its in the bucket
                if check_if_file_exists(file_name):
                    link = upload_static_action(new_file_path, newfilename) # upload new file
                    time.sleep(2)
                    delete_file(file_name)
                    print("Old File Deleted!!")
                # if new file upload success delete old file
                # take the link and reupdate here
            else:
                # remove it and upload the given file to cloudflare and replace dont check if it exists becuase it doesnt
                print("Not Cloudflare!")
                link = upload_static_action(new_file_path, newfilename)


            close_add_file_script = '''
            var elements = document.querySelectorAll("a.delete");
            if (elements.length > 0) {
                elements[0].click();
            }
            '''
            driver.execute_script(close_add_file_script)


            # upload new file
            addfilebutton = '''
            var elements = document.querySelectorAll("a.button.insert");
            for (var i = 0; i < elements.length; i++) {
                elements[i].click();
                break;
            }
            '''
            driver.execute_script(addfilebutton)

            file_download_url_change = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "file_url"))).find_element(By.CLASS_NAME, "input_text") 
            driver.execute_script("arguments[0].scrollIntoView(true);", file_download_url_change)
            driver.execute_script("arguments[0].click;", file_download_url_change)
            file_download_url_change.clear()
            file_download_url_change.send_keys(link)

            try:
                file_download_name_change = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "file_name"))).find_element(By.CLASS_NAME, "input_text") # removing filename and adding Download as name
                driver.execute_script("arguments[0].scrollIntoView(true);", file_download_name_change)
                driver.execute_script("arguments[0].click;", file_download_name_change)
                file_download_name_change.clear()
                file_download_name_change.send_keys("Download")
            except:
                pass

            break

        except Exception as e:
            if check_4 == 2:
                driver.quit()
                return ["Error Updating the file", ""]
        
            time.sleep(3)
            check_4 += 1


    # save changes/update
    check_last = 0
    while True:
        try:
            save2 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "publish")))
            driver.execute_script("arguments[0].scrollIntoView(true);", save2)
            driver.execute_script("arguments[0].click();", save2)
            time.sleep(60)
            break

        except Exception as e:
            if check_last == 2:
                driver.quit()
                return ["Error When Saving Changes", str(e)]

            time.sleep(5)
            check_last += 1

    try:
        WebDriverWait(driver, 150).until(EC.text_to_be_present_in_element_value((By.ID, 'publish'), 'Update'))
        print("Updated!")
    except:
        driver.quit()
        return ["Error Publishing Completion", ""]
            
    # try:
    #     regenerate_button = WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.ID, "regen_dl_permissions_all_users")))
    #     driver.execute_script("arguments[0].scrollIntoView(true);", regenerate_button)
    #     driver.execute_script("arguments[0].click();", regenerate_button)
    #     time.sleep(30)
    # except:
    #     pass
    # time.sleep(30)

    # Return T

    if has_virus:
        driver.quit()
        return [True, "Virus"]
    else:
        driver.quit()
        return [True, True]

    
    
# modify return error as an underline or color for the owner to identify


# update_product("21282", "9.4.1", "04.09.2024", main_path+"21282.zip", [0,0], login_to_wordpress()[1])