import sys
import json
import time
import requests
import datetime
import os
from pathlib import Path

def isBanned(email, password):
    url = "https://api.epics.gg/api/v1/auth/login?categoryId=1&gameId=1"

    payload = "{\"email\":\""+email+"\",\"password\":\""+password+"\"}"
    headers = {
        'Accept': "*/*",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'Referer': "https://app.epics.gg/",
        'Content-Type': "application/json",
        'X-User-JWT': "",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    #print(response.text)

    if json.loads(response.text)['success']:
        return False
    elif json.loads(response.text)['errorCode'] == 'user_banned':
        return True;

accounts_folder = "accounts"

for arg in sys.argv:
	if arg.startswith("-l"):
		accounts_folder = sys.argv[sys.argv.index(arg) + 1]


pathlist = Path("accounts").glob('**/*.json')
for path in pathlist:
     # because path is object not string
    path_in_str = str(path)
    file = open(path, "r")
    file_json = file.read()
    account = json.loads(file_json)
    try:
        print("("+account['email']+"): " + str(isBanned(account['email'], account['password'])))
        time.sleep(0.5)
        #_thread.start_new_thread( os.system, (ex, ) )
    except:
        print("Rate limit; waiting 90 seconds...")
        time.sleep(90)
