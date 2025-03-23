from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
import re
import json
from datetime import datetime, timezone, timedelta
import argparse


# IMPORTANT YOU NEED TO CONFIGURE THE PROFILE_PATH AND CHROME_PROFILE ACCORDING TO YOUR DEVICE

profile_path = r"<YOUR_OWN_PATH>" #For example C:\Users\<USER>\AppData\Local\Google\Chrome\User Data
chrome_profile = "<YOUR_OWN_PROFILE>" #For example Profile 1 


# Headed browser incase the user isn't login to Xiaomi Cloud yet
def needToAuthenticate():

    chrome_service = Service(ChromeDriverManager().install())
    options = Options()

    options.add_argument("--log-level=3") 
    options.add_argument("--silent")  
    options.add_argument("--disable-logging")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={chrome_profile}")
    return webdriver.Chrome(service=chrome_service, options=options)


# Using Headless browser to check if the user has existing token in Xiaomi CLoud
def alreadyAuthenticated():

    chrome_service = Service(ChromeDriverManager().install())
    options = Options()

    options.add_argument("--log-level=3")
    options.add_argument("--silent") 
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-features=EnableMLModel")
    options.add_argument("--headless")
    options.add_argument("--disable-logging")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={chrome_profile}")
    return webdriver.Chrome(service=chrome_service, options=options)


# Gets the needed cookies to extract all of the user notes
def getCookies():

    driver = alreadyAuthenticated()
    driver.get("https://account.xiaomi.com/pass/serviceLogin?")
    time.sleep(3)
    #print(driver.current_url)

    if "/service/account" in driver.current_url:
        print("[+]Authenticated already...")
        
        cookies = driver.get_cookies()
        with open("cookie.txt", "w") as cookie_file:
            for cookie in cookies:
                if cookie["name"] == "userId":
                    userId = f"userId={cookie['value']}"
                    cookie_file.write(userId + "\n")

        print("[+]userId saved to cookie.txt")

        driver.get("https://us.i.mi.com/note/h5")
        time.sleep(3)
        cookies = driver.get_cookies()


        with open("cookie.txt", "a") as cookie_file:
            for cookie in cookies:
                if cookie["name"] == "serviceToken":
                    serviceToken = f"serviceToken={cookie['value']}"
                    cookie_file.write(serviceToken + "\n")

        print("[+]serviceToken saved to cookie.txt")

    elif "/login/password" in driver.current_url:

        print("[/]Please Authenticate First.")
        driver.quit()
        driver = needToAuthenticate()
        driver.get("https://account.xiaomi.com/pass/serviceLogin?")

        while "service/login" in driver.current_url:
            print(driver.current_url)
            time.sleep(1)
        
        time.sleep(3)
        cookies = driver.get_cookies()
        with open("cookie.txt", "w") as cookie_file:
            for cookie in cookies:
                if cookie["name"] == "userId":
                    userId = f"userId={cookie['value']}"
                    cookie_file.write(userId + "\n")

        print("[+]userId saved to cookie.txt")

        driver.get("https://us.i.mi.com/note/h5")
        time.sleep(3)
        current_url = driver.current_url

        if "verifyPhone" in current_url:
            print("OTP verification page detected.")

            while "verifyPhone" in driver.current_url:
                print("Enter your OTP...")
                time.sleep(1) 

            print("OTP completed")

            cookies = driver.get_cookies()
            with open("cookie.txt", "a") as cookie_file:
                for cookie in cookies:
                    if cookie["name"] == "serviceToken":
                        serviceToken = f"serviceToken={cookie['value']}"
                        cookie_file.write(serviceToken + "\n")

            print("[+]serviceToken saved to cookie.txt")

        else:
            cookies = driver.get_cookies()
            with open("cookie.txt", "a") as cookie_file:
                for cookie in cookies:
                    if cookie["name"] == "serviceToken":
                        serviceToken = f"serviceToken={cookie['value']}"
                        cookie_file.write(serviceToken + "\n")

            print("[+]serviceToken saved to cookie.txt")

    print("ADFSGJKNDFJGHKLJNGHLKERTMNGHLERMHLRTKGNSLDKDFNDKLFNGHLKGN")
    #time.sleep(5)
    driver.quit()


# Export all of Xiaomi Notes
def getNotes():

    # Read the userId and serviceToken from cookie.txt and assign it to a variable
    with open("cookie.txt") as file:
        cookies = dict(line.strip().split("=", 1) for line in file if "=" in line)

    userId = cookies.get("userId")
    serviceToken = cookies.get("serviceToken")

    #print(userId)
    #print(serviceToken)

    print("[/]Retrieving All of Note ID")


    url = "https://us.i.mi.com//note/full?"
    cookieHeader = {"serviceToken": serviceToken, "userId": userId}

    allNotes = requests.get(url, cookies=cookieHeader)
    #print(allNotes.content)

    json_response = allNotes.json()
    entries = json_response.get("data", {}).get("entries", [])

    return cookieHeader, [entry["id"] for entry in entries if "id" in entry]

    

def exportNotes(cookieHeader, note_ids):

    #print(note_ids)

    base_url = "https://us.i.mi.com/note/note/"

    for id_value in note_ids:

        # Full Note URL
        note_url = f"{base_url}{id_value}" 
        response = requests.get(note_url, cookies=cookieHeader)
        data =response.json()

        # Gets the Title of the Note
        title_data = data["data"]["entry"]["extraInfo"]
        title_value = json.loads(title_data) 
        title = title_value["title"].strip() 

        # Extract timestamps and format them in preferred Timezone
        utc_offset = timezone(timedelta(hours=args.tzone))
        create_date = datetime.fromtimestamp(int(data["data"]["entry"]["createDate"]) / 1000, tz=utc_offset).strftime('%Y-%m-%d %H:%M:%S UTC+{}'.format(args.tzone))
        modify_date = datetime.fromtimestamp(int(data["data"]["entry"]["modifyDate"]) / 1000, tz=utc_offset).strftime('%Y-%m-%d %H:%M:%S UTC+{}'.format(args.tzone))


        # Gets the Content of the Note
        content_raw = data["data"]["entry"]["content"]
        content = re.findall(r'<text[^>]*>(.*?)<\/text>', content_raw)
        if not content:
            content = [content_raw.strip()]

        note = f"**Title:** {title}\n\n" \
                        f"**Created Time:** {create_date}\n\n" \
                        f"**Modified Time:** {modify_date}\n\n" \
                        + "\n\n".join(content)
        
        # Replace invalid characters with "_" or name it "title_bank" if title is empty
        filename = re.sub(r'[\/:*?"<>|]', '_', title.strip()) or "title_blank"

        # Name blank titles
        base_filename = filename 
        counter = 1
        while os.path.exists(f"{filename}.md"):
            filename = f"{base_filename}_{counter}"
            counter += 1

        filename += ".md"

        # Save the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(note)
        print(f"[+]Note Saved to {filename}")
    print("[+]Done Extracting All of Your Notes!!!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Extract and save Xiaomi Cloud Notes :D")
    parser.add_argument("-d", "--date", action="store_true", help="Includes created and modified date")
    parser.add_argument("-tz", "--tzone", type=int, default=8, metavar="TZ",help="Set timezone offset (Default is UTC+8.)")
    args = parser.parse_args()

    getCookies()
    if os.path.exists("./cookie.txt"):
        cookieHeader, note_ids = getNotes()
        exportNotes(cookieHeader, note_ids)
    else:
        print("[X]Problem in getting the cookies!!!")

