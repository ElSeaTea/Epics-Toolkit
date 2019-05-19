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

def getPacks(jwt_token):
    url = "https://api.epics.gg/api/v1/packs/user?categoryId=1&gameId=1"

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
    return json.loads(response.text)['data']['packs']

def openPack(jwt_token, pack_id):
	url = "https://api.epics.gg/api/v1/packs/open?categoryId=1&gameId=1"

	payload = "{\"packId\":"+str(pack_id)+"}"
	headers = {
		'Accept': "application/json",
		'Accept-Language': "en-US,nl;q=0.7,en;q=0.3",
		'Referer': "https://app.epics.gg/csgo/opening?pack=" + str(pack_id),
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



username = ""
password = ""
log_to_file = False
time_wait_rate_limit = 90
time_wait_loop = 1

for arg in sys.argv:
	if arg.startswith("-l"):
		log_to_file = True
	elif arg.startswith("-r"):
		time_wait_rate_limit = sys.argv[sys.argv.index(arg) + 1]
	elif arg.startswith("-t"):
		time_wait_loop = sys.argv[sys.argv.index(arg) + 1]
	elif arg.startswith("-u"):
		username = sys.argv[sys.argv.index(arg) + 1]
	elif arg.startswith("-p"):
		password = sys.argv[sys.argv.index(arg) + 1]
		

jwt = getJWT(username, password)

#print(jwt)

packs_ids = []
packs = getPacks(jwt)

failed_packs = [] #Packs failed (because of rate limit)

for p in packs:
	packs_ids.append(p['id'])

for pid in packs_ids:
	try:
		pack = openPack(jwt, pid)

		print("Opened pack: " + str(pid))

		if log_to_file:
			file_path = 'opened_packs/' + username
			file_name = str(pid) + ".json"

			if not os.path.exists(file_path):
				os.makedirs(file_path)

			file = open(file_path + '/' + file_name, 'w')
			file.write(json.dumps(pack))
			file.close()

		time.sleep(time_wait_loop)

	except:
		print("Opening of pack (" + pid + ") failed because of rate limit, Waiting " + time_wait_rate_limit + " seconds...")
		failed_packs.append(pid)
		time.sleep(time_wait_rate_limit)

while len(failed_packs) > 0:
	print("Retrying failed packs...")
	for pid in failed_packs:
		try:
			pack = openPack(jwt, pid)

			print("Opened pack: " + str(pid))

			failed_packs.remove(pid)

			if log_to_file:
				file_path = 'opened_packs/' + username
				file_name = str(pid) + ".json"

				if not os.path.exists(file_path):
					os.makedirs(file_path)

				file = open(file_path + '/' + file_name, 'w')
				file.write(json.dumps(pack))
				file.close()

			time.sleep(time_wait_loop)

		except:
			print("Opening of pack (" + pid + ") failed because of rate limit, Waiting " + time_wait_rate_limit + " seconds...")
			time.sleep(time_wait_rate_limit)
