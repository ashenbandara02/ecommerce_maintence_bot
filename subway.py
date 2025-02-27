import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SPREADSHEET_ID = "1gk0zIcgSlerR_2a4KlMckKmiJC-sE5QhaiFACil_Ges"
SAMPLE_RANGE_NAME = "Sheet1!A1:F"


def connection_executor(creds):
    """Build Connection for data Reading"""
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])
        if values:
            service.close()
            return values
        else:
            service.close()
            return False
        
    except Exception as err:
        with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
            err_log.write(f"• {err} \n\n")
        
        try:
            service.close()
        except:
            pass

        return False


def get_product_id(creds, demolink, version=""):
    """
    
    Getting Product Id with Demolink and Check for version same or only get product id
    Returns:-

    Value : Id
    False : Product was already Updated
    None : No Such Product
    """
    # Make Connection
    values = connection_executor(creds)
    if not values:
        time.sleep(60)
        values = connection_executor(creds)

    if values:
        for row in values[1:]:
            row_check = False
            try:
                row_check = row[2]
            except:
                row_check = False # Means Product Present without a demo link

            if row_check != False:
                if row and row[2] == demolink:
                    if version != "":
                        if row[1] != version:
                            # return the Product Id
                            return row[0]
                        else:
                            # return Product Already Updated previously
                            return False
                    else:
                        # return the product Id
                        return row[0]
    else:
        return "SubwayConnectionLoss"

def find_row_index_by_id(creds, target_id):
    """Gets the Index of the Row with Id"""
    values = connection_executor(creds)
    if not values:
        time.sleep(60)
        values = connection_executor(creds)


    if values:
        for index, row in enumerate(values):
            if row and len(row) >= 1 and row[0] == str(target_id):  # Assuming ID is in the 1st column (index 0)
                return index
            

def id_presence(creds, target_id):
    """Find Whether Product with Id Exists"""
    values = connection_executor(creds)
    if not values:
        time.sleep(60)
        values = connection_executor(creds)

    if values:
        for row in values[1:]:
            if row[0] == str(target_id):
                return True
        
        return False
    

def url_adder(creds, demolink, sitename, url):
    """

    With DemoLink Search the Site for Any Product 
    If product Present , Goto Site name Section and check for the url if the url is present it skips else it adds the url

    Returns

    True: Url Added/Updated
    False: Unable to Update
    None: Product Not Present

    """
    product_id = get_product_id(creds, demolink)
    if product_id is None:
        return None
    
    values = connection_executor(creds)
    if not values:
        time.sleep(60)
        values = connection_executor(creds)

    if values:
        sites = (values[0])[3:]
        the_row = None
        for row in values[1:]:
            if row[0] == str(product_id):
                the_row = row
                break

        if the_row is not None:
            if sitename in sites:
                if url not in the_row:
                    #          [0, 1, 2] in the list
                    # [0, 1, 2, 3, 4, 5] <-
                    # so 0 + 3 = 3, 1 + 3 = 4, 2 + 3 = 5
                    index_of_site = sites.index(sitename)
                    index_of_site_in_sheet = index_of_site + 3

                    # checking if url is present
                    try:
                        if the_row[index_of_site_in_sheet] == url:
                            # Now We Skip
                            return True
                        else:
                            raise IndexError

                    except IndexError as e:
                        # Now We Add the Url to the Corresponding place
                        row_index = find_row_index_by_id(creds, the_row[0])
                        cell_range = f"Sheet1!{chr(ord('A') + index_of_site_in_sheet)}{row_index + 1}"

                        service = None

                        try:
                            service = build("sheets", "v4", credentials=creds)
                            sheet = service.spreadsheets()
                            body = {"values": [[url]]}
                            result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=cell_range, body=body,
                                                            valueInputOption="RAW").execute()

                        except Exception as err:
                            with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
                                err_log.write(f"• {err} \n\n")

                            if service:
                                service.close()

                            return False

                        finally:
                            if service:
                                service.close()
                else:
                    return True
            else:
                with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
                    err_log.write(f"• {sitename} : {url} Site Name is Not Found In ExcelSheet\n\n")
                return False
        else:
            return None


def update_row_columns_by_id(creds, target_id, column_indices, new_values, sitename, product_url):
    """
    Updating a Product According to Given Columns and Data
    
    The Function takes a product that needs to be updated, and it directly updated the version no and however if the 
    product update is from wpshop and if that url box is empty or the site name thats new then it replaces or adds the site url to the field and complete and returns

    False: Error
    None: Cant find the Product Index with that Id
    True: Update Complete

    """
    service = None
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        row_index = find_row_index_by_id(creds, target_id)

        if row_index is None:
            return None 

        cell_ranges = [f"Sheet1!{chr(ord('A') + col_index)}{row_index + 1}" for col_index in column_indices]
        body = {"values": [new_values]}
        for cell_range in cell_ranges:
            result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=cell_range, body=body, valueInputOption="RAW").execute()

    except Exception as err:
        with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
            err_log.write(f"• {err} \n\n")
        
        return False
    
    finally:
        if service:
            service.close()

    # Check if the website - url present and if not add it
    values = connection_executor(creds)
    if not values:
        time.sleep(60)
        values = connection_executor(creds)

    if values:
        sites = (values[0])[3:]
        the_row = None
        for row in values[1:]:
            if row[0] == str(target_id):
                the_row = row
                break

        if the_row is not None:
            if sitename in sites:
                if product_url[0] not in the_row:
                    #          [0, 1, 2] in the list
                    # [0, 1, 2, 3, 4, 5] <-
                    # so 0 + 3 = 3, 1 + 3 = 4, 2 + 3 = 5
                    index_of_site = sites.index(sitename)
                    index_of_site_in_sheet = index_of_site + 3

                    # checking if url is present
                    try:
                        if the_row[index_of_site_in_sheet] == product_url[0]:
                            # Now We Skip
                            return True
                        else:
                            raise IndexError
                        
                    except IndexError as e:
                        # Now We Add the Url to the Corresponding place
                        row_index = find_row_index_by_id(creds, the_row[0])
                        cell_range = f"Sheet1!{chr(ord('A') + index_of_site_in_sheet)}{row_index + 1}"

                        service = None

                        try:
                            service = build("sheets", "v4", credentials=creds)
                            sheet = service.spreadsheets()
                            body = {"values": [product_url]}
                            result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=cell_range, body=body,
                                                        valueInputOption="RAW").execute()

                        except Exception as err:
                            with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
                                err_log.write(f"• {err} \n\n")

                            if service:
                                service.close()
                            
                            return True

                        finally:
                            if service:
                                service.close()
    return True


def add_product(creds, product_values):
    """
    product values = [id, version, demolink, sitename, url]
    ["91232132", "1.21.123", "lolaub.cem", "WPSHOP", "Test.com"]

    The Function Takes a Product Details to BE Added Checks if its Already Exists(demolink/id) if not it adds the product to excel and returns 

    True: product Added
    None: Similar Id/ Demolink having product exists
    False: Error

    """
    product_exits_id = get_product_id(creds, product_values[2])
    p_check_verify = False

    if product_exits_id is not None:
        p_check_verify = True
    if id_presence(creds, product_values[0]):
        p_check_verify = True

    if not p_check_verify:
        try:
            service = build('sheets', 'v4', credentials=creds)

            payload = [product_values[0], product_values[1], product_values[2]]

            # Site Belongs to
            if product_values[3] == "WPSHOP":
                payload.append(product_values[4])
            elif product_values[3] == "PLUGINTHEME":
                payload.append("")
                payload.append(product_values[4])
            elif product_values[3] == "WORDPRESSIT":
                payload.append("")
                payload.append("")
                payload.append(product_values[4])
            else:
                with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
                    err_log.write(f"• Unknown Site Name {product_values[3]} \n\n")
                service.close()
                return False
            
            body = {
                'values': [payload]
            }

            result = service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='Sheet1',
                body=body,
                valueInputOption="RAW"
            ).execute()
            
            service.close()
            return True
        
        except Exception as err:
            with open("subwayerror_log.txt", "a", encoding="utf-8") as err_log:
                err_log.write(f"• {err} \n\n")
            service.close()
            return False

    else:
        return None

