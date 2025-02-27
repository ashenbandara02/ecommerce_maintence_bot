import requests
import json
import os

main_path = "/home/ProjectExcel/"
#main_path = "B:/Work/Work/Ezine.lk/ProjectExcel/"


file_path = os.path.join(main_path+'subpy', 'admin_data.json')
with open(file_path, "r") as user_credentials:
    user_data = json.load(user_credentials)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie':'wordpress_test_cookie=WP Cookie check'}


# URL for the login action
login_url = "https://wptoolmart.com/chamarawp/"

def login_to_wordpress():
    payload = {
        'log': user_data['wptoolmart']['email'],
        'pwd': user_data['wptoolmart']['password'],
        'rememberme': 'forever', # if you want to be remembered
        'wp-submit': 'Log In',
        'redirect_to': 'https://wptoolmart.com/chamarawp/',
        'testcookie': '1'
    }

    # Creating a session to persist the login state
    with requests.Session() as session2:
        post = session2.post(login_url, data=payload, headers=headers)
        if post.ok and "Dashboard" in post.text:
            print("[ /u2713 ] WptoolMart Login Was Successfull!!")
            cookies = session2.cookies.get_dict()
            session2.close()
            return [True, cookies]
        else:
            session2.close()
            return [False, ""]