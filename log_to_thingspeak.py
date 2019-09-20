"""log_to_thingspeak.py

This module provides data logging to Thingspeak.

"""

import time
import json
import requests
import config

base_url = 'https://api.thingspeak.com/update.json?api_key='+config.ts_api_key

def update_status_log(airtemp,humidity,tanktoptemp,tankbtmtemp,pump_status,airpump_status):
	payload = {
		"field1": "{0:5.1f}".format(airtemp),
		"field2": "{0:5.1f}".format(humidity),
		"field3": "{0:5.1f}".format(tanktoptemp),
		"field4": "{0:5.1f}".format(tankbtmtemp),
		"field5": pump_status,
		"field6": airpump_status
	}
	try:
		response = requests.post(base_url, data=json.dumps(payload), headers={'content-type':'application/json'})
	except:
		return 500

	return response.status_code
