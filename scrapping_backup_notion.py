import os
import time
import platform
import json
import shutil
import logging
import zipfile
from datetime import datetime
import tarfile
import random
import urllib.request
from zipfile import ZipFile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService


def login_to_notion(email, password):
    try:
        logging.info("Logging in Notion")
        # Open the Notion login page
        driver.get('https://www.notion.so/login')
        # Wait for the page to load completely.
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Enter your email address..."]')))
        # Email
        email_input = driver.find_element(By.XPATH, '//*[@placeholder="Enter your email address..."]')
        email_input.send_keys(email)
        time.sleep(round(random.uniform(0, 2), 1))
        driver.find_element(By.XPATH, '//div[text()="Continue"]').click()
        time.sleep(1.5)

        # Password
        password_input = driver.find_element(By.XPATH, '//*[@placeholder="Enter your password..."]')
        password_input.send_keys(password)
        time.sleep(round(random.uniform(0, 2), 1))
        driver.find_element(By.XPATH, '//div[text()="Continue with password"]').click()

        # Wait for the page to load completely after logging in.
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[text()="Settings & members"]')))
        logging.info("Successful login")
    except Exception as e:
        logging.exception("An error has occurred in the authentication phase: %s", e)

def generate_export():

    # Click on the option "Settings & Members".
    settandmembers_div = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[text()="Settings & members"]')))
    driver.execute_script("arguments[0].click();", settandmembers_div)
    logging.info("Accessed to Settings & members")

    # Wait until the "Settings" item is present and visible before clicking on it, then click it
    settings_div = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Settings"]')))
    driver.execute_script("arguments[0].click();", settings_div)
    logging.info("Accessed to Settings")
    time.sleep(1)

    # Scrolling
    element = driver.find_element(By.XPATH, '//div[text()="Export all workspace content"]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    logging.info('Scrolling')
    time.sleep(1)

    # Click on the "Export all workspace content" option.
    driver.find_element(By.XPATH, '//div[text()="Export all workspace content"]').click()
    logging.info('Accessed to Export all workspace content')

    # Click on the "Export" option
    driver.find_element(By.XPATH, '//div[text()="Export"]').click()
    logging.info("Accessed to Export")

    logging.info("Downloading...")

    try:
        # Esperar a que el archivo se descargue completamente
        wait = WebDriverWait(driver, 60) # 1m de espera
        zip_file_locator = (By.XPATH, f"//a[contains(@href, '.zip') and not(contains(@href, '.crdownload'))]")
        zip_file_element = wait.until(EC.presence_of_element_located(zip_file_locator))
        
        # Esperar a que el enlace sea visible
        wait.until(EC.visibility_of(zip_file_element))
        
        filename = zip_file_element.get_attribute("href").split("/")[-1]
        filepath = os.path.join(download_path, filename)

        logging.info("ZIP file download completed.")
    except:
        logging.warning(f"Omitted: Error timeout")
    finally:
        time.sleep(15)
        driver.execute_script("window.open('','_self').close();")
        driver.quit()

    #Get the path of the most recently downloaded file
    filename_path = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
    logging.info(f"Export downloaded: {os.path.basename(filename_path)}")

    return os.path.join(download_path,filename_path)


def process_output(filename_path):
    new_original_backup_path =  os.path.join(TARGET_PATH, os.path.basename(filename_path))

    EXPORT_FILENAME = "notion_export-" + today + ".zip"
    base_name = os.path.join(TARGET_PATH, "notion_export-")
    today_path = os.path.join(base_name + today + ".zip")
    
    logging.info("Leaving only the most recent backup")
    # Make sure to keep only the 2 most recent backups.
    backups = [d for d in os.listdir(TARGET_PATH) if "notion_export" in d]
    
    if not os.path.exists(today_path):
        if len(backups) >= 2:
            os.remove(base_name + datetime.strftime(min([datetime.strptime(str(back.split('export-')[1].replace('.zip','')),'%d-%m-%Y') for back in backups]),'%d-%m-%Y') + '.zip')
    
    # Moving the export to the target path
    try:
        shutil.move(filename_path, TARGET_PATH)
        logging.info("The file has been moved correctly")
    except FileNotFoundError:
        logging.error("The file was not found in the specified path")
    except Exception as e:
        logging.error(f"An error has occurred: {str(e)}")

    try:
        extracted_folder_name = ""

        logging.info("Extracting files from export")
        # Change to the directory where the file is located
        os.chdir(TARGET_PATH)

        # Extract the main ZIP file and the internal archive
        with zipfile.ZipFile(new_original_backup_path, 'r') as zip_ref:
            zip_info_list = zip_ref.infolist()
            internal_zip_filename = zip_info_list[0].filename
            with zip_ref.open(internal_zip_filename) as internal_zip:
                with zipfile.ZipFile(internal_zip, 'r') as internal_zip_ref:
                    internal_zip_ref.extractall()
                    # Get the name of the extracted folder
                    extracted_folder_name = os.path.splitext(os.path.splitext(internal_zip_filename)[0])[0].replace('-Part-1', '')

        extracted_backup_path = os.path.join(TARGET_PATH,extracted_folder_name)

        # Removing previous zip
        os.remove(new_original_backup_path)

        if data["REMOVE_IDS"]:
            removing_identifiers(extracted_backup_path, today_path)
        else:
            zipper(extracted_backup_path, today_path)

            logging.info("Cleaning of temporary files")
            # Cleaning of temporary files
            shutil.rmtree(extracted_backup_path)

        logging.info(f"File Processed: {EXPORT_FILENAME}")
        logging.info("Backup Completed!")

    except Exception as e:
        logging.exception("An error has occurred in the processing phase: %s", e)


def removing_identifiers(today_path : str, today_file : str):
    logging.info("Removing Identifiers...")
    ids_files = []
    
    for base, dirs, files in os.walk(today_path):
        for file in files:
            if file.endswith('.md') or file.endswith('.csv'):
                files_pattern = file.split(" ")[-1].split(".")[0]
                ids_files.append(files_pattern)
            
    ids_files = list(set(ids_files))
    
    temp_dirs = os.walk(today_path, topdown=False)
    for root, dirs, files in temp_dirs:
        for i in dirs:
            directory = os.path.join(root,i)
            try:
                os.rename(directory,directory.replace(directory.split(" ")[-1],""))
            except (FileExistsError,FileNotFoundError): # log file
                with open(os.path.join(TARGET_PATH, "log.txt"),'a', encoding="utf8") as f:
                    f.write(directory + '\n')
                
    
    temp_file = os.walk(today_path, topdown=False)
    for root, dirs, files in temp_file:
        for file in files:
            if file.endswith('.md') or file.endswith('.csv'):
                file_path = os.path.join(root,file)
                new_path = file_path.replace(" "+file_path.split(" ")[-1].split(".")[0],"")
                
                lines = []
                with open(file_path,'r', encoding="utf8") as f:
                    lines = f.readlines()
                rem = False
                try:
                    with open(new_path, "w", encoding="utf8") as f:
                        for line in lines:
                            for idn in ids_files:
                                line = line.replace("%20"+idn,"")
                            f.write(line)
                            rem = True
                except:
                    with open(os.path.join(TARGET_PATH, "log.txt"),'a', encoding="utf8") as f:
                        f.write(new_path + '\n')
                    rem = False
                if rem and os.path.exists(new_path):
                    os.remove(file_path)
                else:
                    with open(os.path.join(TARGET_PATH, "log.txt"),'a', encoding="utf8") as f:
                        f.write("FAILING" + new_path + '\n')

    zipper(today_path, today_file)
    
    logging.info("Cleaning of temporary files")
    shutil.rmtree(today_path)


def zipper(origin_path_folder, target_path_file):
    logging.info("Compressing export files in a zip file with formatted name")
    #Compress to a final zip.
    with zipfile.ZipFile(target_path_file, "w", zipfile.ZIP_DEFLATED) as zip:
        # Scroll through all the files and subdirectories in the folder
        for root, dirs, files in os.walk(origin_path_folder):
            for file in files:
                # Add each file to the zip file
                file_path = os.path.join(root, file)
                zip.write(file_path, os.path.relpath(file_path, origin_path_folder))

if __name__ == "__main__":

    # Import config
    data = {}
    json_file_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json'))
    with open(json_file_path, encoding='utf-8') as file:
        data = json.load(file)

    ## Global variables ##
    TARGET_PATH = data["TARGET_PATH"]
    today = datetime.today().strftime('%d-%m-%Y')
    log_dat = datetime.today().strftime('%Y-%m-%d')

    # Basic configuration of the registry
    if not os.path.exists(data["DEBUG_PATH"]):
        os.makedirs(data["DEBUG_PATH"], mode=0o777)

    logging.basicConfig(filename=os.path.join(data["DEBUG_PATH"], f'debug-{log_dat}.log'),
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    # Console registry configuration
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    ##################### Driver management #################

    # Download Firefox driver
    try:
        if platform.system() == 'Windows':
            driver_path = os.path.join(os.getcwd(), 'geckodriver.exe')
            if not os.path.isfile(driver_path):
                logging.info("Installing Geckodrive")
                url = 'https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-win64.zip'
                with urllib.request.urlopen(url) as response, open('geckodriver.zip', 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                with ZipFile('geckodriver.zip', 'r') as zipObj:
                    zipObj.extractall(os.getcwd())
                os.remove('geckodriver.zip')
            else:
                logging.info("Geckodrive ready!")
        else:
            driver_path = os.path.join(os.getcwd(), 'geckodriver')
            if not os.path.isfile(driver_path):
                logging.info("Installing Geckodriver")
                url = 'https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux64.tar.gz'
                with urllib.request.urlopen(url) as response, open('geckodriver.tar.gz', 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                with tarfile.open('geckodriver.tar.gz', 'r:gz') as tarObj:
                    tarObj.extractall(os.getcwd())
                os.remove('geckodriver.tar.gz')
            else:
                logging.info("Geckodrive ready!")
    except Exception as e:
        logging.exception("An error occurred in the download phase of the webdriver: %s", e)

    # Driver options
    options = Options()
    # Configure download options in Firefox
    download_path = data["DOWNLOAD_PATH"]
    options.set_preference("browser.charset.default", "UTF-8")
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", download_path)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    options.add_argument("-headless")

    # Start Firefox driver
    try:
        if platform.system() == 'Windows':
            logging.info("Initializing the driver")
            firefox_service = FirefoxService(executable_path=driver_path)
            driver = webdriver.Firefox(service=firefox_service, options=options)
        else:
            logging.info("Initializing the driver")
            driver = webdriver.Firefox(executable_path=driver_path, options=options)
    except Exception as e:
        logging.exception("An error has occurred in the initialization phase of the webdriver: %s", e)

    ########################################################

    # Main workflow #
    login_to_notion(data["EMAIL"], data["PASSWORD"])
    filename_path = generate_export()
    process_output(filename_path)
