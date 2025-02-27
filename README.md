# EcommerceProject

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)

**EcommerceProject** is an automated system for managing a WooCommerce store (`wptoolmart.com`) by scraping product updates from external sites (`wpshop.net`, `plugintheme.net`), syncing data with a Google Spreadsheet, storing files in Cloudflare R2, and updating WordPress products via Selenium. It runs on a 6-hour schedule, logs changes, and sends detailed HTML email reports.

---

## Overview

This project automates the process of keeping an e-commerce store up-to-date by:
- Scraping product changelogs from source sites.
- Comparing versions and deciding to add new products or update existing ones.
- Managing product data in a Google Spreadsheet.
- Uploading files to Cloudflare R2 storage.
- Modifying WooCommerce products using Selenium.
- Generating changelogs and sending email reports.

Key components include scheduling, authentication, data syncing, file management, WordPress automation, and reporting.

---

## Features

- **Scheduled Execution**: Runs every 6 hours via `tmux`.
- **Multi-Source Scraping**: Pulls data from `wpshop.net` and `plugintheme.net`.
- **Google Sheets Integration**: Tracks products in a spreadsheet.
- **Cloudflare R2 Storage**: Stores and serves product files.
- **WordPress Automation**: Adds/updates WooCommerce products.
- **Error Handling**: Logs issues to text files (`subwayerror_log.txt`, `errors.txt`).
- **Email Reporting**: Sends HTML reports with success/failure details.

---

## Prerequisites

- **Python 3.9+**
- **Dependencies**: Install via `requirements.txt` (see below).
- **System Setup**:
  - `tmux` for scheduling (Ubuntu: `sudo apt install tmux`).
  - Chrome browser and ChromeDriver (managed via `webdriver_manager`).
- **Accounts/Credentials**:
  - Google Sheets API (OAuth2 credentials: `credentials.json`).
  - Cloudflare R2 (access keys).
  - Gmail SMTP (app-specific password).
  - WordPress (`wptoolmart.com`), `wpshop.net`, `plugintheme.net` logins.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/EcommerceProject.git
   cd EcommerceProject
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   Create a `requirements.txt` with:
   ```
   boto3
   botocore
   tqdm
   selenium
   webdriver_manager
   requests
   beautifulsoup4
   google-auth-oauthlib
   google-auth-transport-requests
   google-api-python-client
   schedule
   colorama
   smtplib
   ```
   Then run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Credentials**:
   - Place `credentials.json` (Google Sheets API) in the root directory.
   - Create `subpy/admin_data.json` with:
     ```json
     {
       "wptoolmart": {"email": "your@email.com", "password": "yourpass"},
       "wpshop": {"email": "your@email.com", "password": "yourpass"},
       "plugintheme": {"email": "your@email.com", "password": "yourpass"}
     }
     ```
   - Update `cloudflareapi.py` with your R2 credentials.
   - Update `mail_delivery_system.py` with your Gmail credentials.

5. **Set File Paths**:
   - Ensure `/home/ProjectExcel/adder_products/` and `/home/ProjectExcel/updater_products/` exist (or adjust paths in scripts).

---

## Usage

1. **Start the Scheduler**:
   ```bash
   python schedule_run.py
   ```
   This launches the app in a `tmux` session (`my_session`) and runs `update_house.py` every 6 hours.

2. **Monitor Logs**:
   - Check `subwayerror_log.txt` and `errors.txt` in the root directory for issues.

3. **Receive Reports**:
   - Email reports are sent to the address in `mail_delivery_system.py` after each run.

4. **Manual Execution (Optional)**:
   ```bash
   python update_house.py
   ```

---

## Project Structure

```
EcommerceProject/
├── schedule_run.py              # Scheduler for 6-hour runs
├── quickstart.py                # Google Sheets authentication
├── subway.py                    # Google Sheets data operations
├── update_house.py              # Main execution logic
├── wordpress_logger.py          # WordPress login
├── site_logger.py               # Source site logins
├── cloudflareapi.py             # Cloudflare R2 file management
├── wordpress_data_update_api.py # WordPress product updates
├── changelog_creater.py         # Changelog updates
├── wordpress_new_product_adder_api.py # WordPress product additions
├── mail_delivery_system.py      # Email reporting
├── subpy/                       # Submodule directory
│   └── admin_data.json          # Login credentials
├── client_sites/                # Scraping modules (wpshop.py, plugintheme.py - not included)
└── README.md                    # This file
```

---

## How It Works

1. **Scheduling**: `schedule_run.py` triggers `update_house.py` every 6 hours.
2. **Authentication**: Logs into WordPress, source sites, and Google Sheets.
3. **Scraping**: Pulls changelogs from `wpshop.net` and `plugintheme.net`.
4. **Data Sync**: Checks/updates product data in Google Sheets (`subway.py`).
5. **File Handling**: Uploads files to Cloudflare R2 (`cloudflareapi.py`).
6. **WordPress Updates**: Adds (`wordpress_new_product_adder_api.py`) or updates (`wordpress_data_update_api.py`) products.
7. **Reporting**: Updates changelog (`changelog_creater.py`) and sends email (`mail_delivery_system.py`).

---

## Configuration

- **Google Sheets**: Spreadsheet ID in `subway.py` .
- **Cloudflare R2**: Bucket (`storage-wptoolmart`) and endpoint in `cloudflareapi.py`.
- **File Paths**: Adjust in `update_house.py`, `wordpress_data_update_api.py`, and `wordpress_new_product_adder_api.py`.
- **Email**: Sender/recipient in `mail_delivery_system.py`.

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/yourfeature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/yourfeature`).
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with Python, Selenium, and Cloudflare R2.
- Thanks to the open-source community for libraries like `boto3`, `google-api-python-client`, and more.

---
