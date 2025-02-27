# plugintheme_changelog = [{"plugintheme.net/data/product/1": ["1.1.0", "test.com", "PLUGINTHEME"]}]
# changelogs = [
#     [{"www.sample.com": ["1.1.1", "test.com", "PLUGINTHEME"]}],
#     [{"www.abc.com": ["1.1.1", "test.com", "site2"]}, {"www.abc.com": ["1.1.2", "testbravo.com", "site2"]}],
#     [{"www.sample.com": ["1.1.1", "example.com", "site3"]}],
#     [{"www.xyz.com": ["2.0.0", "xyz.com", "site4"]}, {"www.xyz.com": ["2.0.1", "testest.com", "site4"]}],
#     [{"www.abc.com": ["1.1.3", "newtest.com", "site5"]}],
#     [{"www.ubetatta.com": ["1.1.8", "test.com", "PLUGINTHEME"]}]
# ]

import os
import re
import shutil
import sys
import time
import psutil
import requests
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

prev_directory = str(os.path.dirname(os.path.realpath(__file__))).replace("client_sites","")
sys.path.append(prev_directory)

from subpy import site_logger
from subpy.tools.virus_checker import report_scan_activate


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = "https://plugintheme.net/"

# main_path = "F:/Work/projectexcel/"
main_path = "/home/ProjectExcel/"
# adder_products_path = "F:/Work/projectexcel/adder_products/"
# updater_products_path = "F:/Work/projectexcel/updater_products/"
adder_products_path = "/home/ProjectExcel/adder_products/"
updater_products_path = "/home/ProjectExcel/updater_products/"

last_updated_date = ""
with open(main_path+"period.txt", 'r', encoding='utf-8') as period_checkfile:
    last_updated_date = period_checkfile.readlines()[-1]


# Selenium Data
options_cd = Options()
options_cd.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
options_cd.add_argument("--headless") # headless mode *
# options_cd.add_argument("--window-size=1920x1080")
options_cd.add_argument('--no-sandbox')
options_cd.add_argument('--disable-gpu')
options_cd.add_argument('--disable-dev-shm-usage')


def convert_jpg_to_webp(base_name, extension):
    img_path = base_name + '.' + extension
    webp_path = base_name + '.webp'
    try:
        with Image.open(img_path) as img:
            img.save(webp_path, 'WEBP')
    except:
        return False
    
    try:
        os.remove(img_path)
    except:
        print("[ \u2717 ] Bug at Deleting Image Jpg")
    
    return True


def remove_special_characters(input_string): # very important func
    """Removes Unnessasry symbols to avoid crashing during saving a file"""
    translation_table = str.maketrans("", "", "/|\\<>&+?:\"*")
    result_string = input_string.translate(translation_table)

    return result_string.replace(" ", "").replace(",", "")


def get_file_size_in_mb(file_path):
    # file_path = full path
    try:
        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        return int(round(file_size_mb))
    except:
        return None


def demolink_purifier(link):
    return (link.split("?"))[0]


def remove_version_number(title):
    pattern = r'\s\d+(\.\d+|-\w+)*(\.\d+)*\.?\s*$'
    title_without_version = re.sub(pattern, '', title).strip()

    pattern2 = r'\s\.{1,}\d+(\.{1,}\d+)*'
    title_without_version = re.sub(pattern2, '', title_without_version).strip()

    if '..' in title_without_version:
        title_without_version = title_without_version.replace('..', '')
        title_without_version = re.sub(pattern, '', title_without_version).strip()

    if "Yoast WordPress WooCommerce SEO Premium" in title_without_version:
        title_without_version = "WordPress WooCommerce SEO Premium"

    elif "Yoast WordPress Local SEO Premium" in title_without_version:
        title_without_version = "WordPress Local SEO Premium"

    return title_without_version


def format_title(title):
    formatted_title = re.sub(r'[^a-zA-Z0-9\s./&()\-:|#]', '', title)
    formatted_title = formatted_title.replace('.', '-').replace('/', '-').replace('&', '').replace('(', '').replace(')', '')
    formatted_title = re.sub(r'[:#|]+', '-', formatted_title)
    formatted_title = re.sub(r'\s+', '-', formatted_title)
    formatted_title = formatted_title.lower()
    return formatted_title


def format_title_special_case(title):
    if '+' in title:
        title_parts = title.split('+')
        title = title_parts[0].strip()

    return format_title(title)


def convert_date_format(input_date):
    date_obj = datetime.strptime(input_date.strip(), '%d %B %Y')
    formatted_date = date_obj.strftime('%d/%m/%Y')
    return formatted_date


def search_bar_method(name):
    def mini_data_retriver(url):
        try:
            mini_response = requests.get(url, headers=headers)
        except:
            time.sleep(15)
            try:
                mini_response = requests.get(url, headers=headers)
            except Exception as e:
                return [False, False, str(e)]

        if mini_response.status_code == 200:
            p_version = ""
            demolink = ""

            mini_soup = BeautifulSoup(mini_response.content, 'lxml')

            try:
                product_details = mini_soup.find("div", class_="product-short-description")
                ul = product_details.find("ul")
                li_tags = ul.find_all("li")


                for li in li_tags:
                    text = li.get_text(strip=True)
                    if text.startswith("Product Version"):
                        p_version = text.split(":")[1].strip()
                    elif text.startswith("Addon Version"):
                        p_version = text.split(":")[1].strip()
            except:
                pass

            try:
                demolink = mini_soup.find("a", class_="grey-link")['href']
            except:
                pass

            if demolink == "":
                try:
                    demolink = (mini_soup.find("table", class_="urun-detay-buton").find("a"))['href']
                except:
                    pass


            if demolink == "":
                return [False, False, "nodemolink"]


            return [url, p_version, demolink]
        else:
            return [False, False, "Status Code Error"]

    def product_finding_finalize():
        parent_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "autocomplete-suggestions")))
        children_divs = parent_div.find_elements(By.CLASS_NAME, "autocomplete-suggestion")

        if len(children_divs) == 1:
            time.sleep(7)
            
            children = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "autocomplete-suggestion")))
            driver.execute_script("arguments[0].click();", children)
            driver.implicitly_wait(7)

            return mini_data_retriver(driver.current_url)


        for index, children in enumerate(children_divs):
            search_name = children.find_element(By.CLASS_NAME, "search-name")
            if search_name.text == remove_version_number(name):
                the_child = driver.find_elements(By.CLASS_NAME, "autocomplete-suggestion")
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", the_child[index])
                except:
                    pass
                driver.execute_script("arguments[0].click();", the_child[index])

                driver.implicitly_wait(10)
                return mini_data_retriver(driver.current_url)

            else:
                product_name = (remove_version_number(name)).split(" ")
                selected_product_name = children.find_element(By.CLASS_NAME, "search-name").text

                checker = 0

                while checker < 4:
                    for name_part in product_name:
                        if name_part in selected_product_name:
                            checker +=1

                    break

                if checker >= 3:
                    the_child = driver.find_elements(By.CLASS_NAME, "autocomplete-suggestion")
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", the_child[index])
                    except:
                        pass
                    driver.execute_script("arguments[0].click();", the_child[index])

                    driver.implicitly_wait(10)
                    return mini_data_retriver(driver.current_url)
        
        # Goto Search Page and Check
        try:
            search_bar = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "woocommerce-product-search-field-0")))
            driver.execute_script("arguments[0].scrollIntoView(true);", search_bar)
            driver.execute_script("arguments[0].click();", search_bar)
            driver.execute_script("arguments[0].value = '';", search_bar)
            search_bar.send_keys(remove_version_number(name))

            search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "ux-search-submit")))
            driver.execute_script("arguments[0].click();", search_button)

            driver.implicitly_wait(10)

            shop_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "shop-container")))

            if shop_container.text == "No products were found matching your selection.":
                raise Exception
            
            try:
                first_searched_product = shop_container.find_element(By.CLASS_NAME, "woocommerce-LoopProduct-link")
                product_name = (remove_version_number(name)).split(" ")

                checker = 0
                while checker < 4:
                    for name_part in product_name:
                        if name_part in first_searched_product.text:
                            checker +=1

                    break

                if checker >= 1:
                    pass
                else:
                    raise Exception
            except:
                raise Exception

            return mini_data_retriver(first_searched_product.get_attribute("href"))

        except:
            return [False, False, "No Product"]

    def close_all_chromes():
        # Define process names to terminate
        process_names = ["chrome", "chromedriver"]
        
        for process in psutil.process_iter(['pid', 'name']):
            try:
                if process.info['name'] in process_names:
                    # Terminate the process
                    process.terminate()
                    print(f"Terminated: {process.info['name']} (PID: {process.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print("All Chrome instances closed.")

    def clear_chrome_cache_files():
        cache_dir = os.path.expanduser("~/.cache/google-chrome/Default")  # Adjust for Windows/Mac if needed
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"Cleared Chrome cache files: {cache_dir}")
        else:
            print("Chrome cache directory not found.")

    def clear_webdriver_cache():
        cache_dir = os.path.expanduser("~/.wdm")  # WebDriverManager cache directory
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"Cleared WebDriverManager cache: {cache_dir}")
        else:
            print("WebDriverManager cache not found.")

    close_all_chromes()
    clear_chrome_cache_files()
    clear_webdriver_cache()
    
    driver = ""
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_cd)
    except:
        print("Driver Didnt start retrying")
        time.sleep(120)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_cd)

    # with  as driver:
        # service=Service(ChromeDriverManager().install()),
    driver.set_window_size(1920, 1080)
    
    try:
        driver.get(url)
        driver.implicitly_wait(10)
    except:
        # Retry in Few Secounds
        try:
            driver.get(url)
            driver.implicitly_wait(10)
        except:
            return [False, False, "Chrome Opening Error"]
        
    name = (re.sub(r'\(.*?\)', '', name)).replace("  ", " ")

    search_bar = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "woocommerce-product-search-field-0")))
    driver.execute_script("arguments[0].scrollIntoView(true);", search_bar)
    driver.execute_script("arguments[0].click();", search_bar)
    search_bar.send_keys(name)



    # if search results show no products found try other method

    try:
        div_search_name = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-name")))
    except Exception as e:
        driver.save_screenshot('error_screenshot.png')
        return [False, False, "Searching Field Interacting Error 1"]

    if div_search_name.text == "No products found.":
        # Methods
            # # Remove version 
        name = remove_version_number(name)
        search_bar = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "woocommerce-product-search-field-0")))
        driver.execute_script("arguments[0].scrollIntoView(true);", search_bar)
        driver.execute_script("arguments[0].click();", search_bar)
        driver.execute_script("arguments[0].value = '';", search_bar)
        search_bar.send_keys(name)


        try:
            div_search_name = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-name")))
        except:
            driver.save_screenshot('error_screenshot.png')
            return [False, False, "Searching Field Interacting Error 2"]
        
        if div_search_name.text == "No products found.":
            # Remove – replace by - 
            name = name.replace("–", "-") 
            search_bar = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "woocommerce-product-search-field-0")))
            driver.execute_script("arguments[0].scrollIntoView(true);", search_bar)
            driver.execute_script("arguments[0].click();", search_bar)
            driver.execute_script("arguments[0].value = '';", search_bar)
            search_bar.send_keys(name)

            try:
                div_search_name = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-name")))
            except:
                driver.save_screenshot('error_screenshot.png')
                return [False, False, "Searching Field Interacting Error 3"]
            
            if div_search_name.text == "No products found.":
                return [False, False, "No Such Product"]
            else:
                # method 2 worked
                return product_finding_finalize()
        else:
            # method 1 worked
            return product_finding_finalize()
    else:
        return product_finding_finalize()


def find_product_url_demolink_version(name):
    product_location = format_title(remove_version_number(name))

    if "----" in product_location:
        product_location = product_location.replace("----", "-")

    if "---" in product_location:
        product_location = product_location.replace("---", "-")

    if "--" in product_location:
        product_location = product_location.replace("--", "-")



    try:
        response = requests.get(f"{url}shop/{product_location}", headers=headers)
    except:
        time.sleep(15)
        try:
            response = requests.get(f"{url}shop/{product_location}", headers=headers)
        except Exception as e:
            return [False, False, str(e)]

    if response.status_code == 200:
        p_version = ""
        demolink = ""

        soup = BeautifulSoup(response.content, 'lxml')

        try:
            product_details = soup.find("div", class_="product-short-description")
            ul = product_details.find("ul")
            li_tags = ul.find_all("li")


            for li in li_tags:
                text = li.get_text(strip=True)
                if text.startswith("Product Version"):
                    p_version = text.split(":")[1].strip()
                elif text.startswith("Addon Version"):
                    p_version = text.split(":")[1].strip()
        except:
            pass

        try:
            demolink = soup.find("a", class_="grey-link")['href']
        except:
            pass

        if demolink == "":
            try:
                demolink = (soup.find("table", class_="urun-detay-buton").find("a"))['href']
            except:
                pass



        if demolink == "":
            return [False, False, "nodemolink"]
        

        return [f"{url}shop/{product_location}/", p_version, demolink]
    else:
        # 2nd method
        try:
            product_location = format_title(format_title_special_case(remove_version_number(name)))
            reponse_2 = requests.get(f"{url}shop/{product_location}", headers=headers)
            if reponse_2.status_code == 200:
                p_version = ""
                demolink = ""

                soup_2 = BeautifulSoup(reponse_2.content, 'lxml')

                try:
                    product_details = soup_2.find("div", class_="product-short-description")
                    ul = product_details.find("ul")
                    li_tags = ul.find_all("li")


                    for li in li_tags:
                        text = li.get_text(strip=True)
                        if text.startswith("Product Version"):
                            p_version = text.split(":")[1].strip()
                        elif text.startswith("Addon Version"):
                            p_version = text.split(":")[1].strip()
                except:
                    pass

                try:
                    demolink = soup_2.find("a", class_="grey-link")['href']
                except:
                    pass

                if demolink == "":
                    try:
                        demolink = (soup.find("table", class_="urun-detay-buton").find("a"))['href']
                    except:
                        pass



                if demolink == "":
                    return [False, False, "nodemolink"]


                return [f"{url}shop/{product_location}/", p_version, demolink]
            else:
                raise Exception

        except:
            return search_bar_method(name)


def get_data():
    """{product_url: [product_version, product_demolink]}"""
    print("<Getting PluginTheme Changelog - ET per changelog : 10minutes>")
    changelog = []
    with requests.Session() as session_changelog:
        a = False
        for i in range(1, 4):
            try:
                response = session_changelog.get(url+"changelog/", headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "lxml")
                    a = True
            except:
                time.sleep(30)

        if a:
            tables = soup.find_all("table")

            # for table in tables:
            #     new_updated_date = convert_date_format(table.find("tr").text)
            #     date_obj1 = datetime.strptime(last_updated_date, '%d/%m/%Y') # txt datesaved
            #     date_obj2 = datetime.strptime(new_updated_date, '%d/%m/%Y')
            #     if date_obj2 > date_obj1:
            #             print(f"Update Available -> [{new_updated_date}]")
            #             all_rows = table.find_all("tr")[1:]
            #             for i, row in enumerate(all_rows):
            #                 product = row.find_all("td")[1].text
            #                 find_info = find_product_url_demolink_version(product)

            #                 if find_info[0] == False:
            #                     pass
            #                 else:
            #                     changelog.append({str(find_info[0]):[str(find_info[1]), demolink_purifier(str(find_info[2])), "PLUGINTHEME"]})
            for index, table in enumerate(tables):
                new_updated_date = convert_date_format(table.find("tr").text)
                date_obj1 = datetime.strptime(last_updated_date, '%d/%m/%Y') # txt datesaved
                date_obj2 = datetime.strptime(new_updated_date, '%d/%m/%Y')
                if date_obj2 > date_obj1:
                    print(f"Update Available -> [{new_updated_date}]")

                    try:
                        new_updated_date_old = convert_date_format(tables[index+1].find("tr").text)
                        print(f"Update Available -> [{new_updated_date_old}]")
                    except:
                        pass

                    # For current
                    all_rows = table.find_all("tr")[1:]
                    for i, row in enumerate(all_rows):
                        product = row.find_all("td")[1].text
                        find_info = find_product_url_demolink_version(product)

                        if find_info[0] == False:
                            pass
                        else:
                            changelog.append({str(find_info[0]):[str(find_info[1]), demolink_purifier(str(find_info[2])), "PLUGINTHEME"]})

                    # For Previous
                    try:
                        all_rows2 = tables[index+1].find_all("tr")[1:]
                        for i, row in enumerate(all_rows2):
                            product = row.find_all("td")[1].text
                            find_info = find_product_url_demolink_version(product)

                            if find_info[0] == False:
                                pass
                            else:
                                changelog.append({str(find_info[0]):[str(find_info[1]), demolink_purifier(str(find_info[2])), "PLUGINTHEME"]})
                    except:
                        pass

    return changelog


def scrape_to_update_product(url, plugintheme_cookies):
    print("[ \u2713 ] Update Scrape : "+url)

    with requests.Session() as product_session:
        for name, value in plugintheme_cookies.items():
            product_session.cookies.set(name, value)

        max_retries = 3
        delay = 30
        product_response = None
        for attempt in range(max_retries):
            try:
                product_response = product_session.get(url)
            except requests.exceptions.RequestException as e:
                if attempt == 3:
                    return [False, False, False, False, False, f"Connection Error {e}"]
                else:
                    time.sleep(delay)
        
        p_code = None
        try:
            p_code = product_response.status_code
            if p_code != 200:
                raise Exception
        except:
            product_session.close()
            return [False, False, False, False, False, "Get Response Error"]
        
        ###Retrivel###
        product_soup = BeautifulSoup(product_response.content, "lxml")

        if "My account" not in product_soup.text:
            relogin_cookies = site_logger.plugintheme_login()
            if relogin_cookies[0] == True:
                return ["CookieFail", relogin_cookies[1]]
            elif relogin_cookies[0] == False:
                return [False, False, False, False, False, "Cookie Error"]

        #Title
        product_title = ""
        try:
            product_title = (product_soup.find("h1", class_="product-title").text).replace("\n", "").replace("\t", "")
        except:
            pass
        
        #Version
        product_version = ""
        product_last_update = ""
        try:
            product_details = product_soup.find("div", class_="product-short-description")
            ul = product_details.find("ul")
            li_tags = ul.find_all("li")


            for li in li_tags:
                text = li.get_text(strip=True)
                if text.startswith("Product Version"):
                    product_version = text.split(":")[1].strip()
                elif text.startswith("Addon Version"):
                    product_version = text.split(":")[1].strip()
                elif text.startswith("Product Last Updated"):
                    product_last_update = text.split(":")[1].strip()    
        except:
            return [False, False, False, False, False, "Version/UD Error"]


        #file
        file_link = ""
        extension = ""
        try:
            file_link = product_soup.find("a", class_="red-link")['href']
            extension = (file_link.split("/")[-1]).split(".")[-1]
            if len(file_link) == 0:
                raise Exception
        except:
            # error 
            return [False, False, False, False, False, "File Find Error"]
        
        try:
            get_file = product_session.get(file_link)
        except:
            time.sleep(30)
            try:
                get_file = product_session.get(file_link)
            except:
                # error
                return [False, False, False, False, False, "File Download Error"]

        if get_file.status_code == 200:
            version_clean = product_version.replace(".", "").replace("-", "").replace("–", "")
            product_path = updater_products_path + remove_special_characters(product_title.replace(".", "")) + f"-{version_clean}" + f".{extension}"
            
            try:
                with open(product_path, 'wb') as content_file:
                    content_file.write(get_file.content)
            except:
                return [False, False, False, False, False, "File Write Error"]
            
            print("[ \u2713 ] Data Retrieved/ File Downloaded !")
            
            if get_file_size_in_mb(product_path) > 299:
                return [False, False, False, False, False, "SIZE_EXCEED"]
            
            print("[ \u2713 ] File Size Allowed ")

            virus_guard = report_scan_activate(product_path)
            # move to the next func

            if virus_guard == False:
                return [False, False, False, False, False, "Password Protected File"]
            
            print(f"[ \u2713 ] Virus Report files: {virus_guard[0]}, unc size: {virus_guard[1]}")


            if product_last_update != "" and product_last_update != None:
                if product_version != "" and product_version != None:
                    return [product_title + " v" + product_version, product_version, product_last_update, product_path, virus_guard, True]
                
            return [False, False, False, False, False, "Version or Last Updated Date Error"]
        else:
            return [False, False, False, False, False, "File Not Available"]
        



    # Checking FIleSize, Virus


def scrape_new_product(url, plugintheme_cookies):
    """

    returns
    [0]
    [CookieFail, cookies] 
    [True, etc]
    [SIZE_EXCEED]
    [False, "Error"]
    """

    print("[ \u2713 ] New Scrape : "+url)

    with requests.Session() as product_session:
        for name, value in plugintheme_cookies.items():
            product_session.cookies.set(name, value)

        max_retries = 3
        delay = 30
        product_response = None
        for attempt in range(max_retries):
            try:
                product_response = product_session.get(url, headers=headers)
            except requests.exceptions.RequestException as e:
                if attempt == 3:
                    return [False, f"Connection Error {e}"]
                else:
                    time.sleep(delay)
        
        p_code = None
        try:
            p_code = product_response.status_code
            if p_code != 200:
                raise Exception
        except:
            product_session.close()
            return [False, "Get Response Error"]
        
        ##################### 
        sitename = "PLUGINTHEME"
        product_url = str(product_response.url)
        product_price = "3.99"
        #####################

        ###Retrivel###
        product_soup = BeautifulSoup(product_response.content, "lxml")
        

        if "My account" not in product_soup.text:
            print("Cookie Error Encountered! Retrying!!")
            relogin_cookies = site_logger.plugintheme_login()
            if relogin_cookies[0] == True:
                return ["CookieFail", relogin_cookies[1]]
            elif relogin_cookies[0] == False:
                return [False, "Cookie Error"]
            
        #Title
        product_title = ""
        try:
            product_title = (product_soup.find("h1", class_="product-title").text).replace("\n", "").replace("\t", "")
        except:
            return [False, "Title Get Error"]
        

        #Version
        product_version = ""
        product_last_update = ""
        try:
            product_details = product_soup.find("div", class_="product-short-description")
            ul = product_details.find("ul")
            li_tags = ul.find_all("li")


            for li in li_tags:
                text = li.get_text(strip=True)
                if text.startswith("Product Version"):
                    product_version = text.split(":")[1].strip()
                elif text.startswith("Addon Version"):
                    product_version = text.split(":")[1].strip()
                elif text.startswith("Product Last Updated"):
                    product_last_update = text.split(":")[1].strip()    
            
            if product_last_update == "" or product_last_update == None:
                return [False, "Last Updated Date Get Error"]
            if product_version == "" or product_version == None:
                return [False, "Version Get Error"]
        except:
            return [False, "Version/UD Error"]
        

        # Live - Preview
        live_preview = ""
        try:
            live_preview = demolink_purifier(product_soup.find("a", class_="grey-link")['href'])
        except:
            pass

        if live_preview == "":
            try:
                live_preview = demolink_purifier((product_soup.find("table", class_="urun-detay-buton").find("a"))['href'])
            except:
                pass

        if live_preview == "":
            return [False, "Demo link Not Found"]
        

        # Categories
        main_category = ""
        subcategory = ""


        # Image
        image_link = ""
        extension_image = ""
        try:
            image_link = product_soup.find("img", class_="wp-post-image skip-lazy")['src']
            extension_image = (image_link.split("/")[-1]).split(".")[-1]
            if len(image_link) == 0:
                raise Exception
        except:
            return [False, "File Find Error"]
        
        try:
            get_image = requests.get(image_link, headers=headers)
        except:
            time.sleep(30)
            try:
                get_image = requests.get(image_link, headers=headers)
            except:
                # error
                return [False, "Image Download Error"]
        
        image_path = ""

        if get_image.status_code == 200:
            image_sub_path = adder_products_path + remove_special_characters(product_title)
            image_save_path = adder_products_path + remove_special_characters(product_title) + f".{extension_image}"
            image_path = adder_products_path + remove_special_characters(product_title) + ".webp"

            try:
                with open(image_save_path, 'wb') as content_image:
                    content_image.write(get_image.content)
            except:
                return [False, "Image Write Error"]

            convertion = convert_jpg_to_webp(image_sub_path, extension_image) 
            if convertion is not True:
                return [False, "Error Converting to WEBP"]  

            print("[ \u2713 ] Image Downloaded And Converted !")

        else:
            return [False, "Error Getting Image"]


        # file
        file_link = ""
        extension = ""
        try:
            file_link = product_soup.find("a", class_="red-link")['href']
            extension = (file_link.split("/")[-1]).split(".")[-1]
        except:
            # error 
            return [False, "File Find Error"]
        
        try:
            get_file = requests.get(file_link, headers=headers)
        except:
            time.sleep(30)
            try:
                get_file = requests.get(file_link, headers=headers)
            except:
                # error
                return [False, "File Download Error"]

        if get_file.status_code == 200:
            version_clean = product_version.replace(".", "").replace("-", "").replace("–", "")
            product_path = adder_products_path + remove_special_characters(product_title.replace(".", "")) + f"-{version_clean}" + f".{extension}"

            try:
                with open(product_path, 'wb') as content_file:
                    content_file.write(get_file.content)
            except:
                return [False, "File Write Error"]
            
            print("[ \u2713 ] Data Retrieved/ File Downloaded !")
            
            if get_file_size_in_mb(product_path) > 500:
                return ["SIZE_EXCEED"]
            
            print("[ \u2713 ] File Size Allowed ")

            virus_guard = report_scan_activate(product_path)

            if virus_guard == False:
                return [False, "Password Protected File"]

            # move to the next func
            print(f"[ \u2713 ] Virus Report files: {virus_guard[0]}, unc size: {virus_guard[1]}")

            

            
            return [True, product_title, product_price,
                    "", "", main_category, subcategory,
                    product_path, image_path, product_version,
                    product_last_update, live_preview, virus_guard[0],
                    virus_guard[1], sitename, product_url]
                
        else:
            return [False, "File Not Available"]


# # # testing
        
# cook = site_logger.plugintheme_login()[1]

# print(scrape_new_product("https://plugintheme.net/shop/woocommerce-hide-products-categories-prices-payment-and-shipping-by-user-role/", cook))
# # print(scrape_to_update_product("https://plugintheme.net/shop/woocommerce-hide-products-categories-prices-payment-and-shipping-by-user-role/", cook))
