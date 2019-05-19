import sys
import json
import time
import requests
import datetime
import os
from collections import Counter
from pathlib import Path


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

def initiateTrade(slave_jwt, main_uid, main_item, slave_item_array):
    data = {}
    entities = []

    entities.append({'id':main_item, 'type':'card'})

    for item in slave_item_array:
        entities.append({'id':item, 'type':'card'})

    data['user2Id'] = main_uid
    data['user1Balance'] = 0
    data['user2Balance'] = 0
    data['entities'] = entities
    
    payload = json.dumps(data)

    #print(data)

    url = "https://api.epics.gg/api/v1/trade/create-offer?categoryId=1&gameId=1"

    headers = {
        'Accept': "application/json",
        'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
        'Content-Type': "application/json",
        'X-User-JWT': ""+slave_jwt+"",
        'Origin': "https://app.epics.gg",
        'DNT': "1",
        'Connection': "keep-alive",
        'TE': "Trailers",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache",
        'cache-control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    return json.loads(response.text)


def getItemsFromCollection(jwt_token, user_id, collection_id):
    url = "https://api.epics.gg/api/v1/collections/" + str(collection_id) + "/users/" + str(user_id) + "/owned2?categoryId=1&gameId=1"

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
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)['data']['cards']

def getUserIdWithLogin(email, password):
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

    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)['data'][0]['id']

def findBestTradeItem(cards): #Check which card is the most dupicate & worst mint.
    #Check which item has the most dupes
    templates = []
    for card in cards:
        templates.append(card['cardTemplate']['id'])

    most_common_card_template = Counter(templates).most_common()[0][0]

    #Get items with [the most duped] template id
    cards_most = []
    for card in cards:
        if card['cardTemplate']['id'] == most_common_card_template:
            cards_most.append(card)

    #Check for highest mint

    #return card
    return cards_most[0]

currency_collection_id = 1057
purple_collection_id = 893

main_email = ""
main_password = ""

slave_email = ""
slave_password = ""

auto_accept_trade = False
use_accounts_folder = False

for arg in sys.argv:
    if arg.startswith("-a"): #NOT WORKING
        auto_accept_trade = True
    elif arg.startswith("-f"):
        use_accounts_folder = True
    elif arg.startswith("-mU"):
        main_email = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-mP"):
        main_password = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-sU"):
        slave_email = sys.argv[sys.argv.index(arg) + 1]
    elif arg.startswith("-sP"):
        slave_password = sys.argv[sys.argv.index(arg) + 1]

main_jwt = getJWT(main_email, main_password)
main_uid = getUserIdWithLogin(main_email, main_password)

# DEBUG
print(getItemsFromCollection(main_jwt, main_uid, purple_collection_id))
# /DEBUG

if use_accounts_folder:
    print("<<<< USING ACCOUNTS FOLDER >>>>")
    main_used_cards = []
    pathlist = Path("accounts").glob('**/*.json')
    for path in pathlist:
     # because path is object not string
        path_in_str = str(path)
        file = open(path, "r")
        file_json = file.read()
        account = json.loads(file_json)

        slave_jwt = getJWT(account['email'], account['password'])
        slave_uid = getUserIdWithLogin(account['email'], account['password'])

        slave_cards = getItemsFromCollection(slave_jwt, slave_uid, currency_collection_id)

        if len(slave_cards) > 0:
            slave_card_ids = []
            main_collection = getItemsFromCollection(slave_jwt, main_uid, purple_collection_id)

            for card in main_used_cards:
                main_collection.remove(card)

            cheapest_main_card_raw = findBestTradeItem(main_collection)
            cheapest_main_card = cheapest_main_card_raw['id']
            main_used_cards.append(cheapest_main_card_raw)
            cheapest_slave_card = findBestTradeItem(getItemsFromCollection(slave_jwt, slave_uid, purple_collection_id))['id'] # Do this becouse otherwise main will run out of cards ;(


            for card in slave_cards:
                slave_card_ids.append(card['id'])

            slave_card_ids.append(cheapest_slave_card)

            #print(slave_card_ids)
            #print(cheapest_main_card)
            #print(cheapest_slave_card)
            print("("+account['email']+"): Initiating trade...")
            initiateTrade(slave_jwt, main_uid, cheapest_main_card, slave_card_ids)
        else:
            print("("+account['email']+"): No currency cards ;(")

else:
    slave_jwt = getJWT(slave_email, slave_password)
    slave_uid = getUserIdWithLogin(slave_email, slave_password)

    slave_cards = getItemsFromCollection(slave_jwt, slave_uid, currency_collection_id)

    if len(slave_cards) > 0:
        slave_card_ids = []
        cheapest_main_card = findBestTradeItem(getItemsFromCollection(slave_jwt, main_uid, purple_collection_id))['id']
        cheapest_slave_card = findBestTradeItem(getItemsFromCollection(slave_jwt, slave_uid, purple_collection_id))['id'] # Do this becouse otherwise main will run out of cards ;(


        for card in slave_cards:
            slave_card_ids.append(card['id'])

        slave_card_ids.append(cheapest_slave_card)

        print(slave_card_ids)
        print(cheapest_main_card)
        print(cheapest_slave_card)
        print(initiateTrade(slave_jwt, main_uid, cheapest_main_card, slave_card_ids))
    else:
        print("No currency cards ;(")
