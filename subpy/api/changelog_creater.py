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
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def changelog_adder(usucess, asucess, cookies):

    usucess2 = []
    for the_product in usucess:
        for key, value in the_product.items():
            usucess2.append({key: [value[0].replace("<p style='color: red;'>", "").replace("</p>", ""), value[1], value[2]]})

    asucess2 = []
    for the_product in asucess:
        for key, value in the_product.items():
            asucess2.append({key: [value[0].replace("<p style='color: red;'>", "").replace("</p>", ""), value[1], value[2]]})


    changelog = []
    for product in usucess2:
        for key, value in product.items():
            changelog.append(f"<div><span style='font-weight:400;color:red;'>UPDATE</span> : {value[0]}</div>")
    
    for product in asucess2:
        for key2, value2 in product.items():
            changelog.append(f"<div><span style='font-weight:400;color:green;'>NEW</span> : {value2[0]}</div>")

    random.shuffle(changelog)

    for the_product in changelog:
        pass

    options_cd = Options()
    options_cd.add_argument('--headless')
    options_cd.add_argument('--no-sandbox')
    options_cd.add_argument('--disable-dev-shm-usage')
    options_cd.add_argument(f"user-agent={headers['User-Agent']}")
    # driver = webdriver.Chrome(options=options_cd) # Initialize the webdriver

    #### Ubuntu 
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
    driver.maximize_window()

    try:
        driver.get("https://wptoolmart.com/chamarawp/")
    except:
        driver.quit()
        return False

    for key, value in cookies.items():
        driver.add_cookie({
            'name': key,
            'value': value,
            'domain': 'wptoolmart.com',  
            'path': '/',  
        })

    try:
        driver.get("https://wptoolmart.com/wp-admin/admin.php?page=jet-cct-changelog&cct_action=add")
    except:
        return False

    # # fill change log and loop throught the list then add the titles
    try:
        product_container = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "product")))
        driver.execute_script("arguments[0].scrollIntoView();", product_container)

        add_item_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "cx-ui-repeater-add")))
        
        for i in range(0, len(changelog)):
            if i == 0:
                driver.execute_script("arguments[0].click();", add_item_button)
                item = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"title-{i}")))
                driver.execute_script("arguments[0].scrollIntoView();", item)
                driver.execute_script("arguments[0].value = arguments[1];", item, changelog[i])
            else:
                # Print other items in the list
                driver.execute_script("arguments[0].click();", add_item_button)
                item = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"title-{i}")))
                driver.execute_script("arguments[0].scrollIntoView();", item)
                driver.execute_script("arguments[0].value = arguments[1];", item, changelog[i])

        publish = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cx-button.cx-button-primary-style")))
        driver.execute_script("arguments[0].scrollIntoView();", publish)
        driver.execute_script("arguments[0].click();", publish)

        time.sleep(30)
        driver.quit()
        return True
    except:
        return False
