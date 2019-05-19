import sys
import json
import time
import requests
import os
import threading
import _thread
from pathlib import Path

pathlist = Path("accounts").glob('**/*.json')
for path in pathlist:
     # because path is object not string
    path_in_str = str(path)
    file = open(path, "r")
    file_json = file.read()
    account = json.loads(file_json)
    try:
        print("Starting: " + account['email'])
        ex = 'python3 open_all_packs.py -l -u ' + account['email'] + " -p " + account['password']
        #print(ex)
        os.system(ex)
        time.sleep(1)
        #_thread.start_new_thread( os.system, (ex, ) )
    except(KeyboardInterrupt, SystemExit):
        print("KB INTTERUPT")
        cleanup_stop_thread()
        sys.exit()
