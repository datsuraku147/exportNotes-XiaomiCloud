# Export all of your notes from Xiaomi Cloud

I have so many Notes on my phone and since Xiaomi doesn't have a feature to batch-extract them I decided to make a Python script to transfer my Notes from Xiaomi Cloud to my Computer/Laptop :P

If you have any feedback or requests feel free to open a new issue. I hope you have fun using this :D


## Prerequisites
1. **Make sure that your notes have been transferred/synced already to your Xiaomi Cloud**
2. Python3
3. Install all of the needed Python packages: `pip install selenium webdriver-manager requests`

## Usage
1. Clone the repository
2. Open the Python file and Setup your profile_path and chrome_profile: `export.py`
 ```text
profile_path = r"<YOUR_OWN_PATH>" #For example C:\Users\<USER>\AppData\Local\Google\Chrome\User Data
chrome_profile = "<YOUR_OWN_PROFILE>" #For example Profile 1
```

I suggest you use a Profile where you are already logged in to Xiaomi Cloud so the script would directly extract the notes

4. Run the Python file: `python3 export.py`
## Options

```
-h, --help          show this help message and exit
-d, --date          Includes created and modified date
-tz TZ, --tzone TZ  Set timezone offset (Default is UTC+8.)
```

## How it works?

1. It opens up a headless Chrome and checks if you are logged in to Xiaomi Cloud.
   * If yes then it gets the required Cookie to extract all of your Notes to a `.md` file
   * If no then a Chrome Window should pop up and you need to log in first before the script continues (If this is your first time logging in on that Chrome Profile, you might be required to submit an OTP.)
2. The script uses the extracted Cookie(saved to `cookie.txt`)
   * It makes a request to `https://us.i.mi.com//note/full?` to get the ID of your Notes
   * It uses all of the IDs one by one to make a request to `https://us.i.mi.com/note/note/<NOTE_ID>` and get the contents of your Notes
   * Saves each of them to <title_of_your_note>.md (If the Notes doesn't have a title it uses "title_blank.md"

<p align="center">
      <img src="https://github.com/user-attachments/assets/13ad9a64-a726-49b0-91d9-f8ee741d2e4d" width="500" height="500">
</p>




Thanks for checking out this repository and have a nice day :D

-Datsuraku
