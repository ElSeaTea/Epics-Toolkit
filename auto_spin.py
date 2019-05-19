import sys
import json
import time
import requests
import datetime

auto_buy_new_spin = False
default_retry_time = 1 * 60
username = ""
password = ""
use_jwt = False
jwt_token = ""

for arg in sys.argv:
    if arg.startswith("-jwt"):
        jwt_token = sys.argv[sys.argv.index(arg) + 1]
        use_jwt = True
    elif arg.startswith("-u"):
        username = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-p"):
        password = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-a"):
        auto_buy_new_spin = True

def getJWT(email, password):
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

    if json.loads(response.text)['success']:
        return json.loads(response.text)['data']['jwt']
    else:
        return False;

def getSpinnerId(jwt_token):
    url = "https://api.epics.gg/api/v1/spinner?categoryId=1&gameId=1"

    headers = {
        'Accept': "*/*",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'X-User-JWT': "" + jwt_token + "",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, headers=headers)

    return json.loads(response.text)['data']['id']


def runSpinner(spinner_id, jwt_token):
    url = "https://api.epics.gg/api/v1/spinner/spin"

    payload = "{\"spinnerId\":" + str(spinner_id) +"}"
    headers = {
        'Accept': "*/*",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'Referer': "https://app.epics.gg/csgo/spinner",
        'Content-Type': "application/json",
        'X-User-JWT': "" + jwt_token + "",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    return json.loads(response.text)['success']

def buySpin(jwt_token, amount):
    url = "https://api.epics.gg/api/v1/spinner/buy-spin"

    payload = "{\"amount\":" + str(amount) +"}"
    headers = {
        'Accept': "*/*",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'Referer': "https://app.epics.gg/",
        'Content-Type': "application/json",
        'X-User-JWT': "" + jwt_token + "",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    return json.loads(response.text)['success']

def getLatestWin(jwt_token):
    url = "https://api.epics.gg/api/v1/spinner/history?categoryId=1&gameId=1"

    headers = {
        'Accept': "*/*",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'X-User-JWT': "" + jwt_token + "",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, headers=headers)

    return json.loads(response.text)['data']['spins'][0]['name']

def getBalance(jwt_token):
    url = "https://api.epics.gg/api/v1/balance?categoryId=1&gameId="

    headers = {
        'Accept': "*/*",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'X-User-JWT': "" + jwt_token + "",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)['data']

def log(message):
    print(str(datetime.datetime.now()) + ": " + message)
    file = open('logs/auto_spin_'+username+'.log', 'w')
    file.writelines(str(datetime.datetime.now()) + ": " + message)
    file.close()

loops = 10

while True:
    forcestop = open('FORCESTOP', 'r')
    if forcestop.read() == 'STOP':
        log("("+username+") FORCESTOP!")
        forcestop.close()
        exit()
    forcestop.close()

    if not use_jwt:
        if loops > 9:
            jwt_token = getJWT(username, password)
            loops = 0

    if auto_buy_new_spin:
        current_balance = getBalance(jwt_token)
        while current_balance > 9:
            log("("+username+") Balance: " + str(current_balance))
            if buySpin(jwt_token, 1):
                log("("+username+") Bought 1 spin.")
            else:
                log("("+username+") Could not buy 1 spin...")
                break

            current_balance = getBalance(jwt_token)
            log("New balance: " + str(current_balance))
            time.sleep(5)

    result = runSpinner(getSpinnerId(jwt_token), jwt_token)

    if result == True:
        time.sleep(1)
        log("("+username+") You got: " + getLatestWin(jwt_token))
        time.sleep(2)
    else:
        #log("("+username+") waiting " + str(default_retry_time) + " seconds.")
        time.sleep(default_retry_time)
