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
	lock.acquire()
	try:
		response = requests.post(url, data=json.dumps(payload), headers={'content-type':'application/json'}, timeout=15)
		rc = response.status_code
	except Exception as e:
		logging.info("http_post: Error sending to rest API {}".format(url))
		logging.info("http_post: {}".format(e))
		rc = 500
	finally:
		lock.release()

	return rc
