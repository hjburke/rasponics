"""log_to_dweet.py

This module provides data logging to dweet.io.

If you are using the unlocked (free) things, then set the dweet_id in config.py to obfuscate your
thing name.
If you are using locked things, then set the dweet_key in config.py.

"""

import time
#import json
#import requests
import config
#import threading
import http_post as HP
import logging

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

#lock = threading.Lock()

def dweet_update_temps(air_temp,humidity,tank_top_temp,tank_bottom_temp):
	logging.info("dweet_update_temps: Enter")
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"air_temp": "{0:5.1f}".format(air_temp),
		"humidity": "{0:5.1f}".format(humidity),
		"tank_top_temp": "{0:5.1f}".format(tank_top_temp),
		"tank_bottom_temp": "{0:5.1f}".format(tank_bottom_temp)
	}

	#rc = send_to_dweet(thing_name_temp, payload)
	rc = HP.http_post(base_url+thing_name_temp,payload)
	logging.info("dweet_update_temps: Exit")
	return rc

def dweet_update_growbed(GB_duration,GB_direction,GB_last_transition):
	logging.info("dweet_update_growbed: Enter")
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"growbed_cycle_duration":"{d[0]:2}:{d[1]:02}".format(d=divmod(GB_duration,60)),
		"growbed_cycle_direction": 0 if GB_direction=='^' else 180,
		"growbed_cycle_transition_time":time.strftime("%Y-%m-%d %H:%M",time.localtime(GB_last_transition))
	}

	#rc = send_to_dweet(thing_name_growbed, payload)
	rc = HP.http_post(base_url+thing_name_growbed,payload)
	logging.info("dweet_update_growbed: Exit")
	return rc

def dweet_update_equipment(pump_status,airpump_status):
	logging.info("dweet_update_equipment: Enter")
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"pump_status":pump_status,
		"airpump_status":airpump_status
	}
	#rc = send_to_dweet(thing_name_equipment, payload)
	rc = HP.http_post(base_url+thing_name_equipment,payload)

	logging.info("dweet_update_equipment: Exit")
	return rc

#def send_to_dweet(thing_name, payload):
#	print "send_to_dweet: Enter"
#	lock.acquire()
#	try:
#		print "send_to_dweet: about to post {}".format(payload)
#		response = requests.post(base_url+thing_name, data=json.dumps(payload), headers={'content-type':'application/json'})
#		print "send_to_dweet: done with post"
#		rc = response.status_code
#	except Exception as e:
#		print "send_to_dweet: Error sending to rest API"
#		rc = 500
#	finally:
#		print "send_to_dweet: releasing lock"
#		lock.release()
#
#	print "send_to_dweet: Exit"
#	return rc
