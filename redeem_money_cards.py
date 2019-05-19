import sys
import json
import time
import requests
import datetime
import os

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

    #print(response.text)

    if json.loads(response.text)['success']:
        return json.loads(response.text)['data']['jwt']
    else:
        return False;

def getUserID(email, password):
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
        return json.loads(response.text)['data']['user']['id']
    else:
        return False;

def getCards(jwt_token, collection, user_id):
    url = "https://api.epics.gg/api/v1/collections/"+str(collection)+"/users/"+str(user_id)+"/owned2?categoryId=1&gameId=1"

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
    #print(response.text)
    return json.loads(response.text)['data']['cards']

def redeemCard(jwt_token, card_id):
	url = "https://api.epics.gg/api/v1/cards/redeem/"+str(card_id)+"?categoryId=1&gameId=1"

	payload = ""
	headers = {
		'Accept': "application/json",
		'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
		'Content-Type': "application/json",
		'X-User-JWT': ""+jwt_token+"",
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
	#print(payload)

	return json.loads(response.text)


check_card_type = True
currency_card_template = 6144
redeem_currency_category_id = 1057
username = ""
password = ""
jwt = ""
user_id = 0

for arg in sys.argv:
	if arg.startswith("-u"):
		username = sys.argv[sys.argv.index(arg) + 1]
	elif arg.startswith("-p"):
		password = sys.argv[sys.argv.index(arg) + 1]
	elif arg.startswith("-c"):
		check_card_type = False
		

jwt = getJWT(username, password)
user_id = getUserID(username, password)

card_ids = []
cards = getCards(jwt, redeem_currency_category_id, user_id)

for c in cards:
	if check_card_type:
		if c['cardTemplate']['id'] == currency_card_template:
			card_ids.append(c['id'])
	else:
		card_ids.append(c['id'])

for pid in card_ids:
	card = redeemCard(jwt, pid)
	print("Redeemed card: " + str(pid))
	time.sleep(1)
