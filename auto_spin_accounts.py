import sys
import json
import time
import requests
import datetime
from pathlib import Path

timeDelayRateLimit = 90
timeDelayAccount = 1
timeDelayLoop = 300

autoBuyNewSpins = False

for arg in sys.argv:
    if arg.startswith("-tR"):
        timeDelayRateLimit = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-tA"):
        timeDelayAccount = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-tL"):
        timeDelayLoop = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-a"):
        autoBuyNewSpins = True

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


while True:
	pathlist = Path("accounts").glob('**/*.json')
	for path in pathlist:

		accountFile = open(path, 'r')
		accountFileJson = json.loads(accountFile.read())

		try:

			jwt = getJWT(accountFileJson['email'], accountFileJson['password'])

			result = runSpinner(getSpinnerId(jwt), jwt)

			if result:
				print("("+accountFileJson['email']+") You got: " + getLatestWin(jwt))
			else:
				print("("+accountFileJson['email']+") You got: NOTHING ;(")

		except:
			print("Rate Limit... Waiting "+str(timeDelayRateLimit)+" seconds.")
			time.sleep(timeDelayRateLimit)

		#print(path)
		time.sleep(timeDelayAccount)
	print("Loop complete; Waiting "+str(timeDelayLoop)+" seconds!")
