"""http_post.py

This module provides http post with locking.

"""

import time
import json
import requests
import config
import threading
import logging

lock = threading.Lock()

def http_post(url, payload):
#	tid = threading.current_thread()
	tid = "*"
	logging.info("{} http_post: Enter".format(tid))
	lock.acquire()
	try:
		logging.info("{} http_post: about to post {}".format(tid, payload))
		response = requests.post(url, data=json.dumps(payload), headers={'content-type':'application/json'}, timeout=5)
		logging.info("{} http_post: done with post".format(tid))
		rc = response.status_code
	except Exception as e:
		logging.info("{} http_post: Error sending to rest API".format(tid))
		rc = 500
	finally:
		logging.info("{} http_post: releasing lock".format(tid))
		lock.release()
		logging.info("{} http_post: lock released".format(tid))

	logging.info("{} http_post: Exit".format(tid))
	return rc
