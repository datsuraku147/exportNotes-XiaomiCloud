from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
import json


# IMPORTANT YOU NEED TO CONFIGURE THE PROFILE_PATH AND CHROME_PROFILE ACCORDING TO YOUR DEVICE

profile_path = r"<YOUR_OWN_PATH>" #For example C:\Users\<USER>\AppData\Local\Google\Chrome\User Data
chrome_profile = "<YOUR_OWN_PROFILE>" #For example Profile 1 


# Headed browser incase the user isn't login to Xiaomi Cloud yet
def needToAuthenticate():

    chrome_service = Service(ChromeDriverManager().install())
    options = Options()

    #options.add_argument("--log-level=3") 
    #options.add_argument("--silent")  
    options.add_argument("--disable-logging")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={chrome_profile}")
    return webdriver.Chrome(service=chrome_service, options=options)


# Using Headless browser to check if the user has existing token in Xiaomi CLoud
def alreadyAuthenticated():

    chrome_service = Service(ChromeDriverManager().install())
    options = Options()

    #options.add_argument("--log-level=3")
    #options.add_argument("--silent") 
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-features=EnableMLModel")
    options.add_argument("--headless")
    options.add_argument("--disable-logging")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument(f"profile-directory={chrome_profile}")
    return webdriver.Chrome(service=chrome_service, options=options)



# Gets the needed token to extract all of the user notes
def getServiceToken():

    driver = alreadyAuthenticated()
    driver.get("https://account.xiaomi.com/pass/serviceLogin?")


    print(driver.current_url)
    #time.sleep(3)
    if "/service/account" in driver.current_url:
        cookies = driver.get_cookies()
    
        with open("refresh.txt", "w") as cookie_file:
            for cookie in cookies:
                cookie_file.write(f"{cookie['name']}={cookie['value']};\n")

        print("Cookies saved to refresh.txt")

        driver.get("https://us.i.mi.com/note/h5")
        time.sleep(3)
        cookies = driver.get_cookies()


        with open("cookie.txt", "w") as cookie_file:
            for cookie in cookies:
                cookie_file.write(f"{cookie['name']}={cookie['value']};")

        print("Cookies saved to cookie.txt")

    elif "/login/password" in driver.current_url:

        driver.quit()
        driver = needToAuthenticate()
        driver.get("https://account.xiaomi.com/pass/serviceLogin?")

        while "service/login" in driver.current_url:
            print(driver.current_url)
            time.sleep(1)
        
        time.sleep(3)
        cookies = driver.get_cookies()
        with open("refresh.txt", "w") as cookie_file:
            for cookie in cookies:
                cookie_file.write(f"{cookie['name']}={cookie['value']};\n")

        print("Cookies saved to refresh.txt")

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
            with open("cookie.txt", "w") as cookie_file:
                for cookie in cookies:
                    cookie_file.write(f"{cookie['name']}={cookie['value']};")

            print("Cookies saved to cookie.txt")

        else:
            cookies = driver.get_cookies()
            with open("cookie.txt", "w") as cookie_file:
                for cookie in cookies:
                    cookie_file.write(f"{cookie['name']}={cookie['value']};")

            print("Cookies saved to cookie.txt")



    print("ADFSGJKNDFJGHKLJNGHLKERTMNGHLERMHLRTKGNSLDKDFNDKLFNGHLKGN")
    #time.sleep(5)
    driver.quit()   



if __name__ == "__main__":
    getServiceToken()

