"""

This is the Only Py that should be executed when running for updates

"""

import os
import random
import shutil
from datetime import datetime

from subpy.wordpress_logger import login_to_wordpress
from quickstart import authenticate_and_make_connection
from subway import get_product_id, add_product, update_row_columns_by_id

from subpy.api.wordpress_new_product_adder_api import wordpress_add_product
from subpy.api.wordpress_data_update_api import update_product
from subpy.api import changelog_creater
from subpy.api import mail_delivery_system

from client_sites import wpshop
from client_sites import plugintheme

from subpy.site_logger import wpshop_login, plugintheme_login


# wpshop_changelog = ""
# plugintheme_changelog = [{"plugintheme.net/data/product/1": ["1.1.0", "test.com", "PLUGINTHEME"]}]
# changelogs = [
#     [{"www.sample.com": ["1.1.1", "test.com", "PLUGINTHEME"]}],
#     [{"www.abc.com": ["1.1.1", "test.com", "site2"]}, {"www.abc.com": ["1.1.2", "testbravo.com", "site2"]}],
#     [{"www.sample.com": ["1.1.1", "example.com", "site3"]}],
#     [{"www.xyz.com": ["2.0.0", "xyz.com", "site4"]}, {"www.xyz.com": ["2.0.1", "testest.com", "site4"]}],
#     [{"www.abc.com": ["1.1.3", "newtest.com", "site5"]}],
#     [{"www.ubetatta.com": ["1.1.8", "test.com", "PLUGINTHEME"]}]
# ]


# adder_products_path = "F:/Work/projectexcel/adder_products/"
# updater_products_path = "F:/Work/projectexcel/updater_products/"
adder_products_path = "/home/ProjectExcel/adder_products/"
updater_products_path = "/home/ProjectExcel/updater_products/"

# Sites Cookies
wpshop_cookies = wpshop_login()[1]

plugintheme_cookies = plugintheme_login()
if plugintheme_cookies[0] == True:
    print("Plugintheme Login Success!!!")
    plugintheme_cookies = plugintheme_login()[1]
else:
    print("Failed Plugintheme Login ")
    exit()


wpshop_changelog = wpshop.get_data()
plugintheme_changelog = plugintheme.get_data()



# Add More New Rows for new Sites
changelogs = [] # Add All the New Sites(changelog) Here that shud compare versions with plugintheme



content_function_dict = {"WPSHOP": [wpshop, wpshop_cookies], "PLUGINTHEME": [plugintheme, plugintheme_cookies]}


def compare_versions(version_A, version_B):
    """Compare two version strings and return -1 if version_A < version_B, 0 if version_A = version_B, 1 if version_A > version_B.

    Handles various edge cases and invalid formats:
    - Leading/trailing zeros (e.g., "1.02", "005.5.5")
    - Extra dots (e.g., "1.2.3..")
    - Missing components (e.g., "1.2", "121111.1")
    - Non-numeric components (e.g., "1.2.a", "21.2.x")
    - Invalid separators (e.g., "5.5.5.5.11.2", "2..2...52.2")

    Corrects invalid formats before comparison.
    """

    def remove_char_at_index(word, index):
        return word[:index] + word[index + 1:]

    def clean_version(version):
        components = version.split('.')
        for com_index, component in enumerate(components):
            pre_word = component
            zero_before = False
            for letter_index, letter in enumerate(component):
                if letter == "0":
                    if letter_index == 0:
                        pre_word = remove_char_at_index(component, 0)
                        zero_before = True
                    else:
                        pre_word = remove_char_at_index(pre_word, 0)
                        zero_before = True
                else:
                    zero_before = False

                if zero_before == False:
                    break
            components[com_index] = pre_word

        return ".".join(components)

    def is_valid_version(version):
        # Check for invalid separators, non-numeric components, and too many components
        if not all(c.isdigit() for c in version.split('.')):
            return False
        num_components = len(version.split('.'))
        if num_components > 5 or (num_components == 5 and version.split('.')[4] == '0'):
            return False
        return True

    version_A = clean_version(version_A)
    version_B = clean_version(version_B)

    if not is_valid_version(version_A):
        return False
    if not is_valid_version(version_B):
        raise False

    a_components = list(map(int, version_A.split('.')))
    b_components = list(map(int, version_B.split('.')))

    # Ensure components have the same length by padding with zeros
    max_length = max(len(a_components), len(b_components))
    a_components = a_components + [0] * (max_length - len(a_components))
    b_components = b_components + [0] * (max_length - len(b_components))

    for a, b in zip(a_components, b_components):
        if a < b:
            return -1
        elif a > b:
            return 1

    return 0


def scrapper(update_content_holder):
    print("/*Changelog Retrieved Executing Version Comparison !*/")
    ustart = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    wordpress_authentication = login_to_wordpress()

    if wordpress_authentication[0] != True:
        quit()

    total_new_update = len(update_content_holder)
    to_be_updated = 0
    #-------------------------------

    to_be_added = 0
    #-------------------------------

    skipped_already_updated = 0 # [Skipped] {p_key} (New): File Size Limit Exceeded!"

    excel_errors = [] # {p_key} : <strong>Error Occured When Adding to Excel (But New Product Was added to wptoolmart)</strong>"
    other_errors = [] # {p_key} : <strong>{create_wordpress_product[0]}</strong>"

    products_add_success = [] # {p_key: [product_title, product_id, sitename]}
    products_update_success = [] # {p_key: [deploy_update_scrapper[0], current_product_id, p_values[2]]}

    products_add_fail = [] # {p_key: [product_title, product_id, sitename]}
    products_update_fail = [] # {p_key: [product title with version, current_product_id, p_values[2]]}

    #-------------------------------------
    logs = [] # Skipped: <strong>file size error</strong>"
    
    creds = authenticate_and_make_connection()

    # Product Id Comparison
    compareble_list = []
    for changelog in changelogs:
        for dictionary in changelog:
            compareble_list.append(dictionary)

    for product in update_content_holder:
        for product_url, product_info in product.items():
            print(f"\n\n\nProduct: {product_url}")
            # product_info[0] = pversion
            # product_info[1] = pdemolink
            bigger_version_products = [
                {website: version}
                for data_dict in compareble_list
                for website, version in data_dict.items()
                if compare_versions(version[0], product_info[0]) == 1 and version[1] == product_info[1]
            ]

            largest_version_dict = None

            for product_a in bigger_version_products:
                for index, product_b in enumerate(bigger_version_products):
                    if index != 0:
                        product_a_key, product_a_value = next(iter(product_a.items()))
                        product_b_key, product_b_value = next(iter(product_b.items()))
                        if compare_versions(product_a_value[0], product_b_value[0]) == 1:
                            if largest_version_dict == None:
                                largest_version_dict = product_a
                            else:
                                current_product_key, current_product_value = next(iter(largest_version_dict.items()))
                                if compare_versions(current_product_value[0], product_b_value[0]) == -1:
                                    largest_version_dict = product_b

                        elif compare_versions(product_a_value[0], product_b_value[0]) == -1:
                            if largest_version_dict == None:
                                largest_version_dict = product_b

                        elif compare_versions(product_a_value[0], product_b_value[0]) == False:
                            if largest_version_dict == None:
                                largest_version_dict = product
                                logs.append(f"{product_a_key} : Versions Were not compared between Sites : UnTrackable Versions Found eg(beta)-({product_a_value[0]} & {product_b_value[0]})")


            if len(bigger_version_products) > 0:
                if largest_version_dict == None: # more than 1 site having greater version than plugintheme and equal
                    largest_version_dict = bigger_version_products[0]
            elif len(bigger_version_products) == 0:
                largest_version_dict = product
            
            # Now We check if the product is in excel and decide to update/skip/add new
            finalised_product_key, finalised_product_values = next(iter(largest_version_dict.items()))
            product_check = get_product_id(creds, finalised_product_values[1], finalised_product_values[0])


            if product_check == None:
                # Add New Product-Scrapper
                print(">New Product<")
                to_be_added += 1

                p_key, p_values = next(iter(largest_version_dict.items()))
                site_to_retrieve_new = content_function_dict[p_values[2]][0]
                add_new_data_scraper = site_to_retrieve_new.scrape_new_product(p_key, content_function_dict[p_values[2]][1])

                if add_new_data_scraper[0] == "CookieFail":
                    content_function_dict[p_values[2]][1] = add_new_data_scraper[1]
                    add_new_data_scraper = site_to_retrieve_new.scrape_new_product(p_key, content_function_dict[p_values[2]][1])

                if add_new_data_scraper[0] == True:
                    # Create-Add the Product in Wordpress
                    product_title = add_new_data_scraper[1]
                    product_price = add_new_data_scraper[2]
                    product_description = add_new_data_scraper[3]
                    product_file_preview = add_new_data_scraper[4]
                    main_category = add_new_data_scraper[5]
                    category = add_new_data_scraper[6]
                    product_downloadable_file_path = add_new_data_scraper[7]
                    path_for_image_file = add_new_data_scraper[8]
                    product_version = add_new_data_scraper[9]
                    product_last_update = add_new_data_scraper[10]
                    live_preview = add_new_data_scraper[11]
                    virus_guard_value = add_new_data_scraper[12]
                    uncompressed_size = add_new_data_scraper[13]
                    sitename = add_new_data_scraper[14]
                    product_url = add_new_data_scraper[15]
                    create_wordpress_product = wordpress_add_product(product_title, product_price, product_description, product_file_preview, main_category, category, 
                                                                    product_downloadable_file_path, path_for_image_file, product_version, product_last_update, live_preview,
                                                                    virus_guard_value, uncompressed_size, sitename, product_url, wordpress_authentication[1])

                    # Create Excel row
                    if create_wordpress_product[0] == "Cookie fail":
                        wordpress_authentication = login_to_wordpress()
                        if wordpress_authentication[0] == True:
                            #wptoolmart Login has failed
                            create_wordpress_product = wordpress_add_product(product_title, product_price, product_description, product_file_preview, main_category, category, 
                                                                    product_downloadable_file_path, path_for_image_file, product_version, product_last_update, live_preview,
                                                                    virus_guard_value, uncompressed_size, sitename, product_url, wordpress_authentication[1])
                        else:
                            with open("errors.txt", "a", encoding='utf-8') as error_log:
                                error_log.write("\n• Error WPMartLogin: "+str(wordpress_authentication))
                            exit()

                    if create_wordpress_product[0] == True and create_wordpress_product[1] != "":
                        product_id = create_wordpress_product[1]
                        add_to_excel_sheet = add_product(creds, [product_id, product_version, live_preview, sitename, product_url])

                        if add_to_excel_sheet == True:
                            # A-Z Fully Executed Product Succesfull
                            products_add_success.append({p_key: [product_title, product_id, sitename]})
                            print("***Product Added***\n\n")
                            
                        elif add_to_excel_sheet == False:
                            # Error While Adding to Excel
                            products_add_success.append({p_key: [product_title, product_id, sitename]})
                            excel_errors.append(f"{p_key} : <strong>Error Occured When Adding to Excel (But New Product Was added to wptoolmart)</strong>")
                            print("***Product Added (Excel Error)***\n\n")

                        elif add_to_excel_sheet == None:
                            # Similar Id/ Demolink having product exists product was already added to Excel
                            skipped_already_updated += 1
                            excel_errors.append(f"{p_key} : <strong>Similar Product with Same Demolink was Found in Excel. (But New Product Was added to wptoolmart)</strong>")
                            print("***Product Skipped(Similar Product)***\n")
                    else:
                        # Adding to The Wptoolmart is Not Succesfull
                        products_add_fail.append({p_key: [product_title, product_version, sitename]})
                        other_errors.append(f"{p_key} : <strong>{create_wordpress_product[0]}</strong>")
                        print("***Product Failed (wptoolmart Error)***\n\n")
                    
                    # Delete the contents in the adderproducts
                    try:
                        shutil.rmtree(adder_products_path)
                        os.makedirs(adder_products_path, exist_ok=True)
                    except:
                        pass

                elif add_new_data_scraper[0] == "SIZE_EXCEED":
                    skipped_already_updated += 1
                    logs.append(f"[Skipped] {p_key} (New): File Size Limit Exceeded!")
                    print("***Product Skipped (Size Limit)***\n\n")
                    # Delete the contents in the adderproducts
                    try:
                        shutil.rmtree(adder_products_path)
                        os.makedirs(adder_products_path, exist_ok=True)
                    except:
                        pass


                elif add_new_data_scraper[0] == False:
                    print("[Retrieval From Main Site Failed Trying Other Sites!!!]\n")
                    # Initialize Other Sites To Get And Scrape with it if current site was error
                    try:
                        shutil.rmtree(adder_products_path)
                        os.makedirs(adder_products_path, exist_ok=True)
                    except:
                        pass

                    product_title_ = ""
                    product_version_ = ""

                    worked = False
                    while True:
                        try:
                            bigger_version_products.remove(largest_version_dict)
                        except:
                            break

                        if len(bigger_version_products) > 0:
                            # if plugin theme fails some how we goto wpshop and get it from there, if wpshop fails we goto other site and take it from there
                            largest_version_dict = random.choice(bigger_version_products)
                            # We Focus Mainly On Plugin Theme Both PluginTheme and Wpshop is Same So Wpshop is backup site if in case error arise in a product if a list is empty such that no update/new we dont take it to consideration
                            p_key, p_values = next(iter(largest_version_dict.items()))
                            print(f"[Trying ! : {p_values[2]}]")
                            site_to_retrieve_new2 = content_function_dict[p_values[2]][0]
                            add_new_data_scraper2 = site_to_retrieve_new2.scrape_new_product(p_key, content_function_dict[p_values[2]][1])

                            if add_new_data_scraper2[0] == "CookieFail":
                                content_function_dict[p_values[2]][1] = add_new_data_scraper2[1]
                                add_new_data_scraper2 = site_to_retrieve_new2.scrape_new_product(p_key, content_function_dict[p_values[2]][1])

                            if add_new_data_scraper2[0] == True:
                                # Create-Add the Product in Wordpress
                                product_title = add_new_data_scraper2[1]
                                product_price = add_new_data_scraper2[2]
                                product_description = add_new_data_scraper2[3]
                                product_file_preview = add_new_data_scraper2[4]
                                main_category = add_new_data_scraper2[5]
                                category = add_new_data_scraper2[6]
                                product_downloadable_file_path = add_new_data_scraper2[7]
                                path_for_image_file = add_new_data_scraper2[8]
                                product_version = add_new_data_scraper2[9]
                                product_last_update = add_new_data_scraper2[10]
                                live_preview = add_new_data_scraper2[11]
                                virus_guard_value = add_new_data_scraper2[12]
                                uncompressed_size = add_new_data_scraper2[13]
                                sitename = add_new_data_scraper2[14]
                                product_url = add_new_data_scraper2[15]

                                product_title_ = product_title
                                product_version_ = product_version

                                create_wordpress_product2 = wordpress_add_product(product_title, product_price, product_description, product_file_preview, main_category, category, 
                                                                                product_downloadable_file_path, path_for_image_file, product_version, product_last_update, live_preview,
                                                                                virus_guard_value, uncompressed_size, sitename, product_url, wordpress_authentication[1])
                                # Create Excel row
                                if create_wordpress_product2[0] == "Cookie fail":
                                    wordpress_authentication = login_to_wordpress()
                                    if wordpress_authentication[0] == True:
                                        #wptoolmart Login has failed
                                        create_wordpress_product2 = wordpress_add_product(product_title, product_price, product_description, product_file_preview, main_category, category, 
                                                                                product_downloadable_file_path, path_for_image_file, product_version, product_last_update, live_preview,
                                                                                virus_guard_value, uncompressed_size, sitename, product_url, wordpress_authentication[1])
                                    else:
                                        with open("errors.txt", "a", encoding='utf-8') as error_log:
                                            error_log.write("\n• Error WPMartLogin: "+str(wordpress_authentication))
                                        exit()
                                if create_wordpress_product2[0] == True and create_wordpress_product2[1] != "":
                                    product_id = create_wordpress_product2[1]
                                    add_to_excel_sheet = add_product(creds, [product_id, product_version, live_preview, sitename, product_url])

                                    if add_to_excel_sheet == True:
                                        # A-Z Fully Executed Product Succesfull
                                        products_add_success.append({product_url: [product_title, product_id, sitename]})
                                        print("***Product Added***\n\n")
                                        worked = True
                                        break
                                        
                                    elif add_to_excel_sheet == False:
                                        # Error While Adding to Excel
                                        excel_errors.append(f"{p_key} : <strong>Error Occured When Adding to Excel (But New Product Was added to wptoolmart)</strong>")
                                        print("***Product Added(excel error)***\n")
                                        worked = True
                                        break

                                    elif add_to_excel_sheet == None:
                                        # Similar Id/ Demolink having product exists product was already added to Excel
                                        skipped_already_updated += 1
                                        excel_errors.append(f"{p_key} : <strong>Similar Product with Same Demolink was Found in Excel. (But New Product Was added to wptoolmart)</strong>")
                                        print("***Product Skipped(Similar Product)***\n")
                                        break
                                else:
                                    # Adding to The Wptoolmart is Not Succesfull
                                    products_add_fail.append({p_key: [product_title, product_version, sitename]})
                                    other_errors.append(f"{product_title} : <strong>{create_wordpress_product2[0]}</strong>")
                                    print("***Product Failed(wptoolmart error)***\n")
                                    break


                            elif add_new_data_scraper2[0] == "SIZE_EXCEED":
                                logs.append(f"[Skipped] {p_key} (New) : File Size Limit Exceeded! Trying Other Sites For Same Product")
                            

                            elif add_new_data_scraper2[0] == False:
                                # This Site also doesnt work so we proceed to next
                                pass

                            # Delete adderproducts contents
                            try:
                                shutil.rmtree(adder_products_path)
                                os.makedirs(adder_products_path, exist_ok=True)
                            except:
                                pass


                    if not worked:
                        # Error Occured While Getting Data Failed
                        products_add_fail.append({p_key: [product_title_, product_version_, p_values[2]]})
                        other_errors.append(f"{p_key} : <strong>Adding this product was failed by all sites</strong>")
                    
                    try:
                        shutil.rmtree(adder_products_path)
                        os.makedirs(adder_products_path, exist_ok=True)
                    except:
                        pass


            elif product_check == False:
                # Product Exists and Product is up to date!
                skipped_already_updated += 1
                logs.append(f"[Skipped] {finalised_product_key} : Excel Have the Latest Updated Version Already")

                print(">Already Updated<")
                print("***Product Skipped***\n")


            else:
                # Activate Update with productid
                print(">Update Product<")
                to_be_updated += 1
                current_product_id = str(product_check)
                p_key, p_values = next(iter(largest_version_dict.items()))
                site_to_retrieve_update = content_function_dict[p_values[2]][0]
                

                deploy_update_scrapper = site_to_retrieve_update.scrape_to_update_product(p_key, content_function_dict[p_values[2]][1])
                if deploy_update_scrapper[0] == "CookieFail":
                    content_function_dict[p_values[2]][1] = deploy_update_scrapper[1]
                    deploy_update_scrapper = site_to_retrieve_update.scrape_to_update_product(p_key, content_function_dict[p_values[2]][1])

                # title_with_version, new_version, new_p_last_update, product_file_path, virus_guard, Status
                if deploy_update_scrapper[5] is True:
                    deploy_update_worker = update_product(current_product_id, deploy_update_scrapper[1], deploy_update_scrapper[2], deploy_update_scrapper[3], deploy_update_scrapper[4], wordpress_authentication[1])
                    
                    if deploy_update_worker == "Cookie fail":
                        wordpress_authentication = login_to_wordpress()
                        if wordpress_authentication[0] == True:
                            #wptoolmart Login has failed
                            # create instance for wptoolmart to relogin and then update the wptoolmart cookies
                            deploy_update_worker = update_product(current_product_id, deploy_update_scrapper[1], deploy_update_scrapper[2],
                                                    deploy_update_scrapper[3], deploy_update_scrapper[4],
                                                    wordpress_authentication[1])
                        else:
                            with open("errors.txt", "a", encoding='utf-8') as error_log:
                                error_log.write("\n• Error WPMartLogin: "+str(wordpress_authentication))
                            exit()

                    if deploy_update_worker == [True, True]:
                        update_excel = update_row_columns_by_id(creds, current_product_id, [1], [deploy_update_scrapper[1]], p_values[2], [p_key])

                        if update_excel == None:
                            excel_errors.append(f"ID : {current_product_id} : Excel Error : Product with ID not Found")
                        elif update_excel == False:
                            excel_errors.append(f"ID : {current_product_id} : Excel Error : System Error")

                        products_update_success.append({p_key: [deploy_update_scrapper[0], current_product_id, p_values[2]]})

                    elif deploy_update_worker == [True, "Virus"]:
                        update_excel = update_row_columns_by_id(creds, current_product_id, [1], [deploy_update_scrapper[1]], p_values[2], [p_key])

                        if update_excel == None:
                            excel_errors.append(f"ID : {current_product_id} : Excel Error : Product with ID not Found")
                        elif update_excel == False:
                            excel_errors.append(f"ID : {current_product_id} : Excel Error : System Error")

                        products_update_success.append({p_key: ["<p style='color: red;'>"+deploy_update_scrapper[0]+"</p>", current_product_id, p_values[2]]})

                    else:
                        products_update_fail.append({p_key: [deploy_update_scrapper[0], current_product_id, p_values[2]]})
                        other_errors.append(f"{p_key} : {deploy_update_worker[0]} : <strong>{deploy_update_worker[1]}</strong>")

                    # Delete Updateproducts contents
                    try:
                        shutil.rmtree(updater_products_path)
                        os.makedirs(updater_products_path, exist_ok=True)
                    except:
                        pass
                        
                elif deploy_update_scrapper[5] == "SIZE_EXCEED":
                    skipped_already_updated += 1
                    logs.append(f"[Skipped] {p_key} (Update): File Size Limit Exceeded!")

                    # Delete Updateproducts contents
                    try:
                        shutil.rmtree(updater_products_path)
                        os.makedirs(updater_products_path, exist_ok=True)
                    except:
                        pass

                else:
                    # Updating with the best match site failed Use Another available sites
                    
                    # Delete Updateproducts contents
                    try:
                        shutil.rmtree(updater_products_path)
                        os.makedirs(updater_products_path, exist_ok=True)
                    except:
                        pass

                    worked = False
                    while True:
                        try:
                            bigger_version_products.remove(largest_version_dict)
                        except:
                            break

                        # Delete Updateproducts contents
                        try:
                            shutil.rmtree(updater_products_path)
                            os.makedirs(updater_products_path, exist_ok=True)
                        except:
                            pass

                        if len(bigger_version_products) > 0:
                            # if plugin theme fails some how we goto wpshop and get it from there, if wpshop fails we goto other site and take it from there
                            largest_version_dict = random.choice(bigger_version_products)
                            # We Focus Mainly On Plugin Theme Both PluginTheme and Wpshop is Same So Wpshop is backup site if in case error arise in a product if a list is empty such that no update/new we dont take it to consideration
                            p_key, p_values = next(iter(largest_version_dict.items()))
                            site_to_retrieve_update2 = content_function_dict[p_values[2]][0]
                            deploy_update_scrapper2 = site_to_retrieve_update2.scrape_to_update_product(p_key, content_function_dict[p_values[2]][1])

                            if deploy_update_scrapper2[0] == "CookieFail":
                                content_function_dict[p_values[2]][1] = deploy_update_scrapper2[1]
                                deploy_update_scrapper2 = site_to_retrieve_update2.scrape_to_update_product(p_key, content_function_dict[p_values[2]][1])


                            if deploy_update_scrapper2[5] is True:
                                deploy_update_worker2 = update_product(current_product_id, deploy_update_scrapper2[0],
                                                                    deploy_update_scrapper2[1], deploy_update_scrapper2[2],
                                                                    deploy_update_scrapper2[3], deploy_update_scrapper2[4],
                                                                    wordpress_authentication[1])
                                
                                if deploy_update_worker2 == "Cookie fail":
                                    wordpress_authentication = login_to_wordpress()
                                    if wordpress_authentication[0] == True:
                                        #wptoolmart Login has failed
                                        # create instance for wptoolmart to relogin and then update the wptoolmart cookies
                                        deploy_update_worker2 = update_product(current_product_id, deploy_update_scrapper2[0],
                                                                deploy_update_scrapper2[1], deploy_update_scrapper2[2],
                                                                deploy_update_scrapper2[3], deploy_update_scrapper2[4],
                                                                wordpress_authentication[1])
                                    else:
                                        with open("errors.txt", "a", encoding='utf-8') as error_log:
                                            error_log.write("\n• Error WPMartLogin: "+str(wordpress_authentication))
                                        exit()

                                if deploy_update_worker2 == [True, True]:
                                    update_excel = update_row_columns_by_id(creds, current_product_id, [1], [deploy_update_scrapper2[1]], p_values[2], [p_key])

                                    if update_excel == None:
                                        excel_errors.append(f"ID : {current_product_id} : Excel Error : Product with ID not Found")
                                    elif update_excel == False:
                                        excel_errors.append(f"ID : {current_product_id} : Excel Error : System Error")

                                    products_update_success.append({p_key: [deploy_update_scrapper2[0], current_product_id, p_values[2]]})

                                    worked = True
                                    break
                            
                                elif deploy_update_worker2 == [True, "Virus"]:
                                    update_excel = update_row_columns_by_id(creds, current_product_id, [1], [deploy_update_scrapper2[1]], p_values[2], [p_key])

                                    if update_excel == None:
                                        excel_errors.append(f"ID : {current_product_id} : Excel Error : Product with ID not Found")
                                    elif update_excel == False:
                                        excel_errors.append(f"ID : {current_product_id} : Excel Error : System Error")

                                    products_update_success.append({p_key: ["<p style='color: red;'>"+deploy_update_scrapper2[0]+"</p>", current_product_id, p_values[2]]})
                                    
                                    worked = True
                                    break
                                

                                else:
                                    products_update_fail.append({p_key: [deploy_update_scrapper2[0], current_product_id, p_values[2]]})
                                    other_errors.append(f"{p_key} : {deploy_update_worker2[0]} : <strong>{deploy_update_worker2[1]}</strong>")

                                    break

                            elif deploy_update_scrapper2[5] == "SIZE_EXCEED":
                                logs.append(f"[Skipped] {p_key} (Update): File Size Limit Exceeded! Trying Next Site for the same product...")

                            else:
                                # skip it
                                pass
                        else:
                            break

                    # Delete Updateproducts contents
                    try:
                        shutil.rmtree(updater_products_path)
                        os.makedirs(updater_products_path, exist_ok=True)
                    except:
                        pass

                    if not worked:
                        # Error Occured While Getting Data Failed
                        products_update_fail.append({p_key: [deploy_update_scrapper[0], current_product_id, p_values[2]]})
                        other_errors.append(f"{p_key}: ID-{current_product_id} : <strong>Updating this product was failed by all sites(Might Be Due to Password Protection)</strong>")



    ustop = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open("period.txt", 'a', encoding="utf-8") as period_adder:
        period_adder.write("\n"+datetime.now().strftime("%d/%m/%Y"))

    changelog_creater.changelog_adder(products_update_success, products_add_success, wordpress_authentication[1])
    mail_delivery_system.mail_delivery(ustart, ustop, total_new_update, to_be_updated, to_be_added, products_add_success,
                  products_update_success, products_add_fail, products_update_fail,
                  excel_errors, other_errors, logs, skipped_already_updated)
        


if __name__ == "__main__":
    print("Update House Initialize [\u2713]")
    other_holder = None
    if len(plugintheme_changelog) > 0:
        update_content_holder = plugintheme_changelog
        other_holder = wpshop_changelog

    # elif len(plugintheme_changelog) == 0 and len(wpshop_changelog) == 0:
    #     print("No Changelog")
    #     update_content_holder = False
    else:
        update_content_holder = False
    
    # if update_content_holder:
    #     if len(update_content_holder) < len(other_holder): # Imagine plugintheme is not able to retrieve one item from changelog but wpshop does so it gets it from wpshop
    #         urls_a = set(item[list(item.keys())[0]][1] for item in update_content_holder)
    #         urls_b = set(item[list(item.keys())[0]][1] for item in other_holder)

    #         missing_urls = urls_b - urls_a

    #         for item in other_holder:
    #             url = item[list(item.keys())[0]][1]
    #             if url in missing_urls:
    #                 update_content_holder.append(item)
    #                 other_holder.remove(item)


    if update_content_holder:
        scrapper(update_content_holder)


