from bs4 import BeautifulSoup
import requests
import time
import os
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

main_path = "/home/ProjectExcel/"
# main_path = "F:/Work/projectexcel/"
#main_path = "B:/Work/Work/Ezine.lk/ProjectExcel/"

file_path = os.path.join(main_path+'subpy', 'admin_data.json')
with open(file_path, "r") as user_credentials:
    user_data = json.load(user_credentials)

def wpshop_login():
    with requests.Session() as session:
        response = session.get("https://wpshop.net/my-account/")
        soup = BeautifulSoup(response.text, 'lxml')
        csrf_token = soup.find('input', {'name': 'woocommerce-login-nonce'})['value'] #obtain CSRF token after login using requests

        login_data = {
            'username': user_data['wpshop']['email'],
            'password': user_data['wpshop']['password'],
            'rememberme': 'forever', 
            'woocommerce-login-nonce': csrf_token,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }
        # To Avoid Charset Error
        login_response = None
        charset_error = 0
        while True:
            try:
                login_response = session.post("https://wpshop.net/my-account/", data=login_data) # Perform the login request using requests and validation check
                break
            except:
                time.sleep(15)


            if charset_error == 3:
                session.close()
                return [False, False]
            
            charset_error += 1
        
        try:
            if login_response.ok and 'Dashboard' in login_response.text:
                cookies = session.cookies.get_dict()
                session.close()
                return [True, cookies]
            else:
                session.close()
                return [False, ""]
        except:
            session.close()
            return [False, ""]
        

def plugintheme_login():
    with requests.Session() as session_plugintheme:
        response = session_plugintheme.get("https://plugintheme.net/my-account/", headers=headers)
        time.sleep(10)
        soup = BeautifulSoup(response.text, 'lxml')
        # try:   
        #     csrf_token = soup.find('input', {'name': 'woocommerce-login-nonce'})['value'] #obtain CSRF token after login using requests
        # except:
        #     time.sleep(60)
        print(soup.prettify())
        csrf_token = soup.find('input', {'name': 'woocommerce-login-nonce'})['value']

        login_data = {
            'username': user_data['plugintheme']['email'],
            'password': user_data['plugintheme']['password'],
            'rememberme': 'forever', 
            'woocommerce-login-nonce': csrf_token,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }
        # To Avoid Charset Error
        login_response = None
        charset_error = 0
        while True:
            try:
                login_response = session_plugintheme.post("https://plugintheme.net/my-account/", data=login_data, headers=headers) # Perform the login request using requests and validation check
                break
            except:
                time.sleep(15)


            if charset_error == 3:
                session_plugintheme.close()
                return [False, False]
            
            charset_error += 1
        
        try:
            if login_response.ok and 'CHAMARA LAKSHAN' in login_response.text:
                cookies = session_plugintheme.cookies.get_dict()
                session_plugintheme.close()
                return [True, cookies]
            else:
                session_plugintheme.close()
                return [False, ""]
        except:
            session_plugintheme.close()
            return [False, ""]
        