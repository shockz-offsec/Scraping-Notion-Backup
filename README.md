# Scraping-Notion-Backup
This script automates the backup process of Notion data into Markdown and CSV formats, without the need for tokens or the use of private Notion APIs. 
Moreover, the script processes the data to remove any AWS identifiers that may be present in the markdown files, folders, and internal references to other files in the backup.

Can run on both Windows and Linux

> !! At no time is the information (credentials, tokens) used in the script are recompiled.!!

## Requirements & Installation

To use this tool, you need to have the Selenium module installed. You can install it by running the following command in your terminal:

```bash
pip install selenium
```

After that, you can download the repository by running the following commands:

```bash
git clone https://github.com/shockz-offsec/Scraping-Notion-Backup.git
cd Scraping-Notion-Backup
```

### Compatibility

This script is compatible with both Windows and Linux operating systems and requires Python 3.

## Configuration

The script's configuration is defined in the config.json file, which has the following structure:

```json
{
    "REMOVE_IDS": true,
    "DOWNLOAD_PATH": "C:\\Users\\YourUsername\\Downloads",
    "TARGET_PATH": "C:\\path\\to\\your\\backup\\folder",
    "DEBUG_PATH": "C:\\path\\to\\your\\logs\\folder",
    "EMAIL":"your_notion_email",
    "PASSWORD":"your_password"
}
```

* `REMOVE_IDS`: a boolean parameter that indicates whether the script should remove AWS identifiers from the downloaded files.
* `DOWNLOAD_PATH`: the path where the downloaded files will be stored.
* `TARGET_PATH`: the path where the processed backup files will be stored.
* `DEBUG_PATH`: the path where the script logs will be saved.
* `EMAIL`: the email address associated with the Notion account.
* `PASSWORD`: the password associated with the Notion account.

## How it works

The backup process is entirely carried out in the background using web scraping, without requiring any user input. 

The export is downloaded and processed according to the user's choice in the configuration file, which can remove AWS identifiers from markdown files, folders, and internal file references. Old backups are then deleted, leaving only the current and most recent backup. 

The processed export is compressed into a zip file with the format notion_export-dd-mm-yyyy.zip. Additionally, the script generates a log file of all the actions performed during the process, using the format debug-dd-mm-yyyy.log.

The script uses the Firefox webdriver (geckodriver), which is automatically installed during the setup process.

## Usage

```bash
python3 scrapping_backup_notion.py
```

## Automating backups

In Windows, you can automate the script by creating a scheduled task with the Windows Task Scheduler. This can be done by creating a `.bat` file with the following contents:

```batch
@echo off
C:\Python3\python.exe "C:\path\to\scrapping_backup_notion.py"
```
This will allow the script to run automatically at specified intervals without requiring manual intervention.

In Linux you can use Cron for example.
