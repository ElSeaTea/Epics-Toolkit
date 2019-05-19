import sys
import json
import time
import requests
import string
import random
import datetime
import hashlib
import xml.etree.ElementTree as ET

verbose = True

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def getRandomMailDomain():
	domains = []
	url = "https://10minemail.com/request/domains/"
	respone = requests.request("GET", url)
	xml_root = ET.fromstring(respone.text)
	for child in xml_root:
		domains.append(child.text)
	return random.choice(domains)

def getVerfCode(mail_addr):
	response_mail_list_url = "https://10minemail.com/request/mail/id/" + hashlib.md5(mail_addr.encode()).hexdigest()
	response_mail_list = requests.request("GET", response_mail_list_url)

	response_main_list_xml_root = ET.fromstring(response_mail_list.text)

	retrys = 0

	while len(response_main_list_xml_root[0]) < 1: #Wait for mail. TODO: Check if mail is from epic
		if retrys > 5:
			return "000000"
		print('No mail yet, retrying...')
		retrys = retrys+1
		#print(response_mail_list.text)
		time.sleep(1)
		response_mail_list = requests.request("GET", response_mail_list_url)
		response_main_list_xml_root = ET.fromstring(response_mail_list.text)

	for child in response_main_list_xml_root:
		if child[4].text == "noreply@epics.gg": #Check if mail is from Epics
			#print(child[8].text)
			mail_body = child[8].text
			code_first = mail_body[15 :]
			code = code_first[:6]
			return code

	return "000000"

def getVerfCodeInboxKitten(mailKittenRecepient):
	response_mail_list_url = "https://inboxkitten.com/api/v1/mail/list?recipient=" + mailKittenRecepient.lower()

	response_mail_list = requests.request("GET", response_mail_list_url)
	response_mail_list_json = json.loads(response_mail_list.text)
	while len(response_mail_list_json) < 1:
		response_mail_list = requests.request("GET", response_mail_list_url)
		response_mail_list_json = json.loads(response_mail_list.text)
		#print("Waiting for mail: " + str(len(response_mail_list_json)))
		time.sleep(1)

	if response_mail_list_json[0]['message']['headers']['from'] == "noreply@epics.gg":

		mailKey = "sw-" + response_mail_list_json[0]['storage']['key']

		response_email_url = "https://inboxkitten.com/api/v1/mail/getHtml?mailKey=" + mailKey
		response_email = requests.request("GET", response_email_url)

		code_first = response_email.text[15 :]
		code = code_first[:6]

		return code

def createAccount(username, password, email):
	url = "https://api.epics.gg/api/v1/auth/register?categoryId=1&gameId=1"

	payload = "{\"username\": \""+username+"\",\"password\":\""+password+"\", \"email\":\""+email+"\",\"phone\":\"\",\"firstName\":\"\",\"lastName\":\"\"}"
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
	return json.loads(response.text)['success']

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

def verifyAccount(code, jwt_token):
    url = "https://api.epics.gg/api/v1/auth/verify-email?categoryId=1&gameId=1"

    payload = "{\"code\":\"" + code +"\"}"
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

def log(message):
    print(str(datetime.datetime.now()) + ": " + message)
    file = open('logs/account_creator.log', 'w')
    file.write(str(datetime.datetime.now()) + ": " + message + "\n")
    file.close()

def getRandomNames(amount):
	url = "http://names.drycodes.com/"+str(amount)+"?case=lower"
	response = requests.request("GET", url)
	return json.loads(response.text)


loops = 0
loop_for_ever = True
max_loops = 5
use_random_names = False
random_names = []
password = ""

for arg in sys.argv:
	if arg.startswith("-m"):
		loop_for_ever = False
		max_loops = int(sys.argv[sys.argv.index(arg) + 1])
	elif arg.startswith("-r"):
		use_random_names = True
	elif arg.startswith("-p"):
		password = sys.argv[sys.argv.index(arg) + 1]

if use_random_names:
	if loop_for_ever:
		random_names = getRandomNames(50)
	else:
		random_names = getRandomNames(max_loops)

while loops < max_loops or loop_for_ever:
	forcestop = open('FORCESTOP', 'r')
	if forcestop.read() == 'STOP':
		log("FORCESTOP!")
		forcestop.close()
		exit()
	forcestop.close()

	#email_provider = "@mail-finder.net"
	email_provider = getRandomMailDomain()
	if use_random_names:
		email_prefix = random.choice(random_names).lower() + "_" + id_generator(4).lower()
	else:
		email_prefix = id_generator(12).lower()


	try:
		if createAccount(email_prefix, password, email_prefix+email_provider):

			log("Creating account with credentials: " + email_prefix+email_provider + ", " + password)

			jwt = getJWT(email_prefix+email_provider, password)
			time.sleep(0.5)
			verf = getVerfCode(email_prefix + email_provider)
			
			if verifyAccount(verf, jwt):
				#print("email: " + email_prefix+email_provider)
				#print("password: " + password)
				loops = loops + 1

				file = open("accounts/"+email_prefix + ".json", 'w')
				file.write("{\"email\":\""+email_prefix+email_provider+"\",\"password\":\""+password+"\"}")
				file.close()
			else:
				log("Verification ERROR!")
	except:
		print("Exception: Probably a rate error... Waiting 10 seconds...")
		time.sleep(10)
