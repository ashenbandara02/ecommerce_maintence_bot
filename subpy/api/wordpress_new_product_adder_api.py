import random
import re
import os
import string
import sys
import time
from selenium import webdriver
import colorama
from colorama import Fore
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cloudflareapi import upload_static_action

# prev_directory = str(os.path.dirname(os.path.realpath(__file__))).replace("api","")
# sys.path.append(prev_directory)


colorama.init(autoreset=True)

# base_file_local = "F:/Work/projectexcel/adder_products/"
base_file_local = "/home/ProjectExcel/adder_products/"


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_id_with_re(url):
    pattern = r'post=(\d+)'
    match = re.search(pattern, url)
    if match:
        post_id = match.group(1)
        return str(post_id)
    else:
        return None

def wordpress_add_product(product_title, product_price, product_description, product_file_preview, main_category, category, product_downloadable_file_path, path_for_image_file, product_verison, product_last_update, live_preview, virus_guard_value, uncompressed_size, sitename, product_url, wordpress_cookies):
    #Selenium Initiation

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
    

    ############### Rest Of Worker Code #######################
    print(Fore.BLUE + "Product Creation On Work!")
    
    try:
        driver.get("https://wptoolmart.com/chamarawp/")
    except:
        driver.quit()
        return ["Error: Cannot Load Url https://wptoolmart.com/chamarawp/", ""]

    for key, value in wordpress_cookies.items():
        driver.add_cookie({
            'name': key,
            'value': value,
            'domain': 'wptoolmart.com',  
            'path': '/',  
        })

    try:
        driver.get("https://wptoolmart.com/wp-admin/post-new.php?post_type=product")
    except:
        driver.quit()
        return ["Error: Cannot Load Url https://wptoolmart.com/wp-admin/post-new.php?post_type=product", ""]

    # Check for Successful Login
    try:
        WebDriverWait(driver, 60).until(EC.visibility_of_any_elements_located((By.CLASS_NAME , "wp-heading-inline")))
    except:
        driver.quit()
        return ['Cookie fail']

    # Add title
    print("> Adding Title <")
    try:
        title_field = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "title")))
        driver.execute_script("arguments[0].scrollIntoView(true);", title_field)
        driver.execute_script("arguments[0].click();", title_field)
        title_field.clear()
        title_field.send_keys(product_title)
    except:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error Finding the title-box Product or File Was Not Created or Uploaded", ""]

    ### Drafting the File to Get a New Product ID ###
    try:
        draft_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'save-post')))
        driver.execute_script("arguments[0].scrollIntoView(true);", draft_button)
        driver.execute_script("arguments[0].click();", draft_button)
        # ActionChains(driver).move_to_element(draft_button).click().perform()

    except:
        try: 
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error (1) Drafting At First (No Product Or File Added)", ""]
    

    try:
        save_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'save-post')))
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)

        try:
            WebDriverWait(driver, 20).until(
                lambda driver: "button disabled" == save_button.get_attribute("class")
            )
        except:
            pass

        # Wait for the class to change back to "button"
        print("> Draft on Que <")

        WebDriverWait(driver, 100).until(
            lambda driver: "button" == save_button.get_attribute("class")
        )
        print("> Drafted! <")
    except:
        if "action=edit" in str(driver.current_url):
            print("> Drafted! <")
        else:
            try: 
                submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
                driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
                driver.execute_script("arguments[0].click();", submitdelete)
                time.sleep(10)
            except:
                pass
            driver.quit()
            return ["Error (2) Drafting At First (No Product Or File Added)", ""]
    
    ## Rechange the Name of the File
    wptoolmart_post_url = ""
    try:
        wptoolmart_post_url = str(driver.current_url)
        if len(wptoolmart_post_url) < 10:
            raise Exception
    except:
        wptoolmart_post_url = ""
        try: 
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()

    new_product_id =  extract_id_with_re(wptoolmart_post_url)
    if new_product_id is None:
        return ["Error Finding New Product ID", ""]
    
    new_file_path = ""
    try:
        oldfilename = product_downloadable_file_path.split("/")[-1]
        oldfilename_list = oldfilename.split(".")
        oldfilename, extension = oldfilename_list[0], oldfilename_list[1]
        random_key_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        newfilename = oldfilename+"-000"+str(new_product_id)+f"-{random_key_code}"+"."+extension

        os.rename(product_downloadable_file_path, os.path.join(os.path.dirname(product_downloadable_file_path), newfilename))
        new_file_path = base_file_local + newfilename

    except:
        try: 
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass

        driver.quit()
        return ["Error Creating New Product File Name", ""]


    # Add File 
    print("> Adding File <")
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, '_virtual')))
        virtual_button = driver.find_element(By.ID, '_virtual')
        driver.execute_script("arguments[0].scrollIntoView(true);", virtual_button)
        driver.execute_script("arguments[0].click();", virtual_button)

        downloadable_button = driver.find_element(By.ID, '_downloadable')
        driver.execute_script("arguments[0].scrollIntoView(true);", downloadable_button)
        driver.execute_script("arguments[0].click();", downloadable_button)

        try:
            try:
                expiry = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "_download_expiry")))
            except:
                expiry = driver.find_element(By.ID, "_download_expiry")
                
            driver.execute_script("arguments[0].scrollIntoView(true);", expiry)
            driver.execute_script("arguments[0].click();", expiry)
            expiry.send_keys(365)
        except:
            pass

        # insert = driver.find_element(By.CLASS_NAME, "insert")
        # driver.execute_script("arguments[0].scrollIntoView(true);", insert)
        # driver.execute_script("arguments[0].click();", insert)

        # upload_file_button = driver.find_element(By.CLASS_NAME, "upload_file_button")
        # driver.execute_script("arguments[0].click();", upload_file_button)

        # select_upload_section = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "menu-item-upload")))
        # driver.execute_script("arguments[0].click();", select_upload_section)

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

        link = upload_static_action(new_file_path, newfilename)
        if "pub" not in link:
            raise Exception
        
        file_download_url_change.send_keys(link)

        try:
            file_download_name_change = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "file_name"))).find_element(By.CLASS_NAME, "input_text") # removing filename and adding Download as name
            driver.execute_script("arguments[0].scrollIntoView(true);", file_download_name_change)
            driver.execute_script("arguments[0].click;", file_download_name_change)
            file_download_name_change.clear()
            file_download_name_change.send_keys("Download")
        except:
            pass
    
    
    except:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass

        driver.quit()
        return ["Error (virtual/downloadable/upload section choose file button)", ""]


    print(Fore.GREEN + "[ \u2713 ] File Uploaded")
    try:
        file_download_name_change = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "file_name"))).find_element(By.CLASS_NAME, "input_text") # removing filename and adding Download as name
        driver.execute_script("arguments[0].scrollIntoView(true);", file_download_name_change)
        driver.execute_script("arguments[0].click;", file_download_name_change)
        file_download_name_change.clear()
        file_download_name_change.send_keys("Download")

        # Add Price
        print("> Adding Price <")
        pricefield = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, '_regular_price')))
        driver.execute_script("arguments[0].scrollIntoView(true);", pricefield)
        pricefield.send_keys(product_price)

        # Setting Limit Purchases to 1 Item Only 
        inventory_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "inventory_options"))).find_element(By.TAG_NAME, "a")
        driver.execute_script("arguments[0].scrollIntoView(true);", inventory_button)
        driver.execute_script("arguments[0].click();", inventory_button)
        individually = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "_sold_individually")))
        driver.execute_script("arguments[0].scrollIntoView(true);", individually)
        driver.execute_script("arguments[0].click();", individually)
    except:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error Occured During - Price/Limit 1 Item Section but ( FILE WAS UPLOADED )", ""]
    


    # Add Main Image
    print("> Adding Main Image <")
    try:
        set_main_image = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'set-post-thumbnail')))
        driver.execute_script("arguments[0].scrollIntoView(true);", set_main_image)
        driver.execute_script("arguments[0].click();", set_main_image)
        upload_image = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'menu-item-upload')))
        driver.execute_script("arguments[0].click()", upload_image)
        input_tag = "//input[starts-with(@id,'html5_')]"
        while True:
            try:
                driver.find_element(By.XPATH, input_tag).send_keys(path_for_image_file)
                break
            except:
                pass
            time.sleep(1)

        uploading_main = False
        percentage = []
        while True:
            try:
                progress_bar = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "media-uploader-status"))).find_element(By.CLASS_NAME, "media-progress-bar").find_element(By.TAG_NAME, "div")
                number_str = progress_bar.get_attribute('style').split()[1]
                number = str(number_str[:-1])
                percentage.append(number)
                if 'width: 100%' in progress_bar.get_attribute('style'):
                    uploading_main = True
                    break
            except: 
                pass
            
        if not uploading_main:
            raise Exception

        time.sleep(60)
        set_image_button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Set product image')]")))
        driver.execute_script("arguments[0].click();", set_image_button)
    
    except Exception as e:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error While Uploading Main Image but ( FILE WAS UPLOADED )", ""]
    

    # Adding product-version, product-last-updated, live-preview, virus-total, uncompressed-size
    print("> Adding Version/Up-Date/Livepreview/Virus-count/SizeInfo <")
    try:
        # product-version
        the_product_version = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product-version")))
        driver.execute_script("arguments[0].scrollIntoView(true);", the_product_version)
        driver.execute_script("arguments[0].click();", the_product_version)

        the_product_version.clear()
        the_product_version.send_keys(product_verison)

        # product-last-updated
        the_product_update = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product-last-updated")))
        driver.execute_script("arguments[0].scrollIntoView(true);", the_product_update)
        driver.execute_script("arguments[0].click();", the_product_update)

        the_product_update.clear()
        the_product_update.send_keys(product_last_update)

        # live-preview
        live_preview_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "live-preview")))
        driver.execute_script("arguments[0].scrollIntoView(true);", live_preview_field)
        driver.execute_script("arguments[0].click();", live_preview_field)

        live_preview_field.clear()
        live_preview_field.send_keys(live_preview)

        # virus-total
        virus_total = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "virus-total")))
        driver.execute_script("arguments[0].scrollIntoView(true);", virus_total)
        driver.execute_script("arguments[0].click();", virus_total)

        virus_total.clear()
        virus_total.send_keys(virus_guard_value)

        # uncompressed-size
        uncompressed_size_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "uncompressed-size")))
        driver.execute_script("arguments[0].scrollIntoView(true);", uncompressed_size_field)
        driver.execute_script("arguments[0].click();", uncompressed_size_field)

        uncompressed_size_field.clear()
        uncompressed_size_field.send_keys(uncompressed_size)

    except:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error in product-version, product-last-updated, live-preview, virus-total, uncompressed-size section", ""]
    
    
    # Add Desciption
    print("> Adding Description <")
    try:
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "content_ifr")))
        driver.execute_script("arguments[0].scrollIntoView(true);", iframe)
        driver.switch_to.frame(iframe)
        tinymce_body_p = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tinymce p:first-of-type")))
        tinymce_body_p.send_keys(product_description)
        driver.switch_to.default_content()
    except:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error While Description Handling but ( FILE/IMAGE WAS UPLOADED )", ""]
    

    # Add File Preview
    print("> Adding Short Description <")
    try:

        iframe_short = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "excerpt_ifr")))
        driver.execute_script("arguments[0].scrollIntoView(true);", iframe_short)
        driver.switch_to.frame(iframe_short)
        tinymce_body_p2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tinymce p:first-of-type")))
        tinymce_body_p2.clear()
        tinymce_body_p2.send_keys(product_file_preview)
        driver.switch_to.default_content()

    except:
        try:
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error While Short Description Handling ( FILE/IMAGE WAS UPLOADED )", ""]


    # # Add Category
    # print("> Adding Categories <")
    # if main_category == "Mockups":
    #     main_category_selector = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'in-product_cat-43')))
    #     driver.execute_script("arguments[0].scrollIntoView(true);", main_category_selector)
    #     driver.execute_script("arguments[0].click();", main_category_selector)
        
    #     if category == "Apparel":
    #         sub_catergory_selector = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'in-product_cat-44')))
    #         driver.execute_script("arguments[0].scrollIntoView(true);", sub_catergory_selector)
    #         driver.execute_script("arguments[0].click();", sub_catergory_selector)
    #     elif category == "Brochure":
    #         sub_catergory_selector = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'in-product_cat-45')))
    #         driver.execute_script("arguments[0].scrollIntoView(true);", sub_catergory_selector)
    #         driver.execute_script("arguments[0].click();", sub_catergory_selector)



    # Publish / Draft
    # published_complete = False
    # try:
    #     publish_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'publish')))
    #     driver.execute_script("arguments[0].scrollIntoView(true);", publish_button)
    #     driver.execute_script("arguments[0].click();", publish_button)

    # except:
    #     try:
    #         submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
    #         driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
    #         driver.execute_script("arguments[0].click();", submitdelete)
    #         time.sleep(10)
    #     except:
    #         pass
    #     driver.quit()
    #     return ["Error Drafting but ( FILE/IMAGE WAS UPLOADED ) error:1", ""]


    # try:
    #     WebDriverWait(driver, 100).until(EC.text_to_be_present_in_element_value((By.ID, 'publish'), 'Update'))
    #     published_complete = True
    # except Exception as e:
    #     try: 
    #         submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
    #         driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
    #         driver.execute_script("arguments[0].click();", submitdelete)
    #         time.sleep(10)
    #     except:
    #         pass
    #     driver.quit()
    #     return ["Error Drafting but ( FILE/IMAGE WAS UPLOADED ) error:2", ""]

    # if published_complete:
    #     wptoolmart_post_url = str(driver.current_url)
    #     driver.quit()

    #     # Intergrate Adding to Excel Here product values = [id, version, demolink, sitename, url]
    #     iD = extract_id_with_re(wptoolmart_post_url)
    
    #     if iD is not None:
    #         excel_process = add_product(authenticate_and_make_connection(), [iD, str(product_verison), live_preview, sitename, product_url])
    #         return [True, excel_process]
    #     else:
    #         return [True, ""]
    
    
    ################### Drafting Part ########################
    try:
        draft_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'save-post')))
        driver.execute_script("arguments[0].scrollIntoView(true);", draft_button)
        driver.execute_script("arguments[0].click();", draft_button)
        # ActionChains(driver).move_to_element(draft_button).click().perform()

    except:
        try: 
            submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
            driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
            driver.execute_script("arguments[0].click();", submitdelete)
            time.sleep(10)
        except:
            pass
        driver.quit()
        return ["Error Drafting but ( FILE/IMAGE WAS UPLOADED ) error:1", ""]
    

    try:
        save_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'save-post')))
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)

        try:
            WebDriverWait(driver, 20).until(
                lambda driver: "button disabled" == save_button.get_attribute("class")
            )
        except:
            pass

        # Wait for the class to change back to "button"
        print("> Draft on Que <")

        WebDriverWait(driver, 100).until(
            lambda driver: "button" == save_button.get_attribute("class")
        )
        print("> Drafted! <")
    except:
        if "action=edit" in str(driver.current_url):
            print("> Drafted! <")
        else:
            try: 
                submitdelete = driver.find_element(By.CLASS_NAME, "submitdelete")
                driver.execute_script("arguments[0].scrollIntoView(true);", submitdelete)
                driver.execute_script("arguments[0].click();", submitdelete)
                time.sleep(10)
            except:
                pass
            driver.quit()
            return ["Error Drafting but ( FILE/IMAGE WAS UPLOADED ) error:2", ""]
    
    return [True, new_product_id]
