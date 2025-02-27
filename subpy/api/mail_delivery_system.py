import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = "wptoolmart7799@gmail.com"
sender_password = "jeto nlzi qjrm tejs"


def item_parser(list_of_items):
    list0 = []
    list1 = []

    for item in list_of_items:
        for key, values in item.items():
            if values[2] == "PLUGINTHEME":
                list0.append(item)
            elif values[2] == "WPSHOP":
                list1.append(item)

    return [list0, list1]



def mail_delivery(ustart, ustop, total_new_update, to_be_updated, to_be_added, products_add_success, products_update_success, 
                  products_add_fail, products_update_fail, excel_errors, other_errors, logs, skipped) -> bool:
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)

        recipient_email = "chamaralakshan7799@gmail.com"
        subject = f"Auto-Update-Mail System"


        add_success = item_parser(products_add_success)
        
        update_success = item_parser(products_update_success)
        
        add_fail = item_parser(products_add_fail)
        
        update_fail = item_parser(products_update_fail)

        # headers
        plugintheme_header = """
        <tr>
            <th colspan="2">PluginTheme</th>
        </tr>
        """
        wpshop_header = """
        <tr>
            <th colspan="2">Wpshop</th>
        </tr>
        """

        # Success_Add
        plugintheme_add = "{}".format(''.join('<tr><td id="green">✓</td><td><a href="{}">{}</a></td></tr>'.format(key, values[0]) for d in add_success[0] for key, values in d.items()))
        wpshop_add = "{}".format(''.join('<tr><td id="green">✓</td><td><a href="{}">{}</a></td></tr>'.format(key, values[0]) for d in add_success[1] for key, values in d.items()))

        # Success_update
        plugintheme_update = "{}".format(''.join('<tr><td id="green">✓</td><td><a href="{}">ID-<strong>{}</strong>: {}</a></td></tr>'.format(key, values[1], values[0]) for d in update_success[0] for key, values in d.items()))
        wpshop_update = "{}".format(''.join('<tr><td id="green">✓</td><td><a href="{}">ID-<strong>{}</strong>: {}</a></td></tr>'.format(key, values[1], values[0]) for d in update_success[1] for key, values in d.items()))

        # Fail_add
        plugintheme_add_fail = "{}".format(''.join('<tr><td id="red">X</td><td><a href="{}">{}</a></td></tr>'.format(key, values[0]) for d in add_fail[0] for key, values in d.items()))
        wpshop_add_fail = "{}".format(''.join('<tr><td id="red">X</td><td><a href="{}">{}</a></td></tr>'.format(key, values[0]) for d in add_fail[1] for key, values in d.items()))

        # Fail_update
        plugintheme_update_fail = "{}".format(''.join('<tr><td id="red">X</td><td><a href="{}">ID-<strong>{}</strong>: {}</a></td></tr>'.format(key, values[1], values[0]) for d in update_fail[0] for key, values in d.items()))
        wpshop_update_fail = "{}".format(''.join('<tr><td id="red">X</td><td><a href="{}">ID-<strong>{}</strong>: {}</a></td></tr>'.format(key, values[1], values[0]) for d in update_fail[1] for key, values in d.items()))

        # Excel Errors
        excel = "{}".format(''.join('<tr><td>{}<td/></tr>'.format(error) for error in excel_errors))
        # Other Errors
        other = "{}".format(''.join('<tr><td>{}<td/></tr>'.format(other_error) for other_error in other_errors))

        # Skipped Section
        skipps = "{}".format(''.join('<tr><td>{}<td/></tr>'.format(log) for log in logs))

        main_body = f"""
        <body>
            <div class="container">
                <h1>Auto-Update-Bot Log</h1>
                <div class="container-2">
                    <p class="info-1">Start Time: {ustart}</p>
                    <p class="info-1">Stop Time: {ustop}</p>
                </div>
                <div class="container-3">
                    <p class="info-1">Total New/Update Present: {total_new_update}</p>
                    <p class="info-1">Total Updates Available: {to_be_updated}</p>
                    <p class="info-1">Total New Available: {to_be_added}</p>
                    <p class="info-1" id="success"><span>Success Updates: </span>{len(products_update_success)}</p>
                    <p class="info-1" id="success"><span>Success New: </span>{len(products_add_success)}</p>
                    <p class="info-1" id="fail"><span>Failed Updates: </span>{len(products_update_fail)}</p>
                    <p class="info-1" id="fail"><span>Failed New: </span>{len(products_add_fail)}</p>
                    <p class="info-1"><span>Skipped: </span>{skipped}</p>
                </div>
                <div class="container-4">
                    <h2>Content List</h2>
                        <div class="container-4-1">
                            <h3>Update List</h3>
                            
                            <table class="content">
                                {plugintheme_header}

                                {plugintheme_update}
                                {plugintheme_update_fail}

                                {wpshop_header}

                                {wpshop_update}
                                {wpshop_update_fail}
                            </table>

                        </div>
                        <div class="container-4-2">
                            <h3>New List</h3>

                            <table class="content">
                                {plugintheme_header}

                                {plugintheme_add}
                                {plugintheme_add_fail}

                                {wpshop_header}

                                {wpshop_add}
                                {wpshop_add_fail}
                            </table>
                        </div>
                </div>

                <div class="container-5">
                    <h2>Error List</h2>
                    <div class="container-5-1">
                        <h3>Main Errors</h3>

                        <table class="content">
                            {other}
                        </table>
                    </div>

                    <div class="container-5-2">
                        <h3>Excel Errors</h3>

                        <table class="content">
                            {excel}
                        </table>
                    </div>
                </div>
                <div class="container-6">
                    <h2>Logs</h2>

                    <table class="content">
                        {skipps}
                    </table>
                </div>
            </div>
        </body>
        """

        head = """<head><style>body{font-family:'Arial',sans-serif;background-color:#f4f4f4;color:#333;margin:20px;}.container,.container-2,.container-3,.container-4,.container-5,.container-6,.container-4-1,.container-4-2,.container-5-1,.container-5-2{max-width:600px;margin:0 auto;margin-bottom:5px;padding:20px;background-color:#fff;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);}.container h1{color:#4285f4;text-align:center;line-height:2;}h3{text-align:center;font-family:Arial,sans-serif;color:#2ecc71;font-weight:300;}.info-1{font-size:16px;font-family:'Helvetica',sans-serif;font-weight:600;line-height:1.6;}#success span{color:green;}#fail span{color:red;}.content{font-family:arial,sans-serif;border-collapse:collapse;width:100%;}td,th{max-width:200px;border:1px solid #dddddd;word-wrap:break-word;text-align:left;padding:8px;}#green{width:20px;color:lightgreen;}#red{width:20px;color:red;}</style></head>"""

        body = f"""
        <html>
            {head}
            {main_body}
        </html>
        """




        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        html_part = MIMEText(body, 'html')
        message.attach(html_part)

        server.sendmail(sender_email, recipient_email, message.as_string())

    return True


# total_new_update = 10
# to_be_updated = 3
# to_be_added = 5
# skipped = 2

# excel_errors = ["test1.com : <strong>Error Occurred When Adding to Excel (But New Product Was added to wptoolmart)</strong>",
#                 "test2.com : <strong>Error Occurred When Adding to Excel (But New Product Was added to wptoolmart)</strong>"]

# other_errors = ["test4.com : <strong>Error: {create_wordpress_product_error1}</strong>",
#                 "test5.com : <strong>Error: {create_wordpress_product_error2}</strong>"]

# products_add_success = [{"test6.com": ["Product 1", "123", "PLUGINTHEME"]}, {"test7.com": ["Product 2", "456", "WPSHOP"]}]

# products_update_success = [{"test8.com": ["Updated Product 1", "789", "PLUGINTHEME"]}, {"test9.com": ["Updated Product 2", "101", "WPSHOP"]}]

# products_add_fail = [{"test10.com": ["Failed Product 1", "111", "PLUGINTHEME"]}, {"test11.com": ["Failed Product 2", "222", "WPSHOP"]}]

# products_update_fail = [{"test12.com": ["Failed Updated Product 1", "333", "PLUGINTHEME"]}, {"test13.com": ["Failed Updated Product 2", "444", "WPSHOP"]}]

# logs = ["Skipped: <strong>file size error</strong>", "Skipped: <strong>file not found</strong>"]


# mail_delivery("1:30pm", "1:55am", total_new_update, to_be_updated, to_be_added, products_add_success, products_update_success, products_add_fail, products_update_fail, excel_errors, other_errors, logs, skipped)
