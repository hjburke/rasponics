"""log_to_dweet.py

This module provides data logging to dweet.io.

If you are using the unlocked (free) things, then set the dweet_id in config.py to obfuscate your
thing name.
If you are using locked things, then set the dweet_key in config.py.

"""

import time
import json
import requests
import config

base_url = 'https://dweet.io/dweet/for/'
thing_name_temp = 'rasponics-temp'
thing_name_growbed = 'rasponics-gb'
thing_name_equipment = 'rasponics-equip'

if (config.dweet_id != ""):
	thing_name_temp += '-'+config.dweet_id
	thing_name_growbed += '-'+config.dweet_id
	thing_name_equipment += '-'+config.dweet_id

if (config.dweet_key != ""):
	thing_name_temp += '?key='+config.dweet_key
	thing_name_growbed += '?key='+config.dweet_key
	thing_name_equipment += '?key='+config.dweet_key

def dweet_update_temps(air_temp,humidity,tank_top_temp,tank_bottom_temp):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"air_temp": "{0:5.1f}".format(air_temp),
		"humidity": "{0:5.1f}".format(humidity),
		"tank_top_temp": "{0:5.1f}".format(tank_top_temp),
		"tank_bottom_temp": "{0:5.1f}".format(tank_bottom_temp)
	}

	try:
		response = requests.post(base_url+thing_name_temp, data=json.dumps(payload), headers={'content-type':'application/json'})
	except:
		return 500

	return response.status_code

def dweet_update_growbed(GB_duration,GB_direction,GB_last_transition):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"growbed_cycle_duration":"{d[0]:2}:{d[1]:02}".format(d=divmod(GB_duration,60)),
		"growbed_cycle_direction": 0 if GB_direction=='^' else 180,
		"growbed_cycle_transition_time":time.strftime("%Y-%m-%d %H:%M",time.localtime(GB_last_transition))
	}

	try:
		response = requests.post(base_url+thing_name_growbed, data=json.dumps(payload), headers={'content-type':'application/json'})
	except:
		return 500

	return response.status_code

def dweet_update_equipment(pump_status,airpump_status):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"pump_status":pump_status,
		"airpump_status":airpump_status
	}

	try:
		response = requests.post(base_url+thing_name_equipment, data=json.dumps(payload), headers={'content-type':'application/json'})
	except:
		return 500

	return response.status_code
