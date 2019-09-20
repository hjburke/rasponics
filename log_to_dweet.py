"""log_to_dweet.py

This module provides data logging to dweet.io.

If you are using the unlocked (free) things, then set the dweet_id in config.py to obfuscate your
thing name.
If you are using locked things, then set the dweet_key in config.py.

"""

import time
import config
import http_post as HP
import logging

base_url = 'https://dweet.io/dweet/for/'
thing_name_temp = 'rasponics-temp'
thing_name_growbed = 'rasponics-gb'
thing_name_equipment = 'rasponics-equip'
thing_name_feeding = 'rasponics-feeding'

if (config.dweet_id != ""):
	thing_name_temp += '-'+config.dweet_id
	thing_name_growbed += '-'+config.dweet_id
	thing_name_equipment += '-'+config.dweet_id
	thing_name_feeding += '-'+config.dweet_id

if (config.dweet_key != ""):
	thing_name_temp += '?key='+config.dweet_key
	thing_name_growbed += '?key='+config.dweet_key
	thing_name_equipment += '?key='+config.dweet_key
	thing_name_feeding += '?key='+config.dweet_key

def dweet_update_temps(air_temp,humidity,tank_top_temp,tank_bottom_temp):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"air_temp": "{0:5.1f}".format(air_temp),
		"humidity": "{0:5.1f}".format(humidity),
		"tank_top_temp": "{0:5.1f}".format(tank_top_temp),
		"tank_bottom_temp": "{0:5.1f}".format(tank_bottom_temp)
	}
	rc = HP.http_post(base_url+thing_name_temp,payload)
	return rc

def dweet_update_growbed(GB_duration,GB_direction,GB_last_transition):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"growbed_cycle_duration":"{d[0]:2}:{d[1]:02}".format(d=divmod(GB_duration,60)),
		"growbed_cycle_direction": 0 if GB_direction=='^' else 180,
		"growbed_cycle_transition_time":time.strftime("%Y-%m-%d %H:%M",time.localtime(GB_last_transition))
	}
	rc = HP.http_post(base_url+thing_name_growbed,payload)
	return rc

def dweet_update_equipment(pump_status,airpump_status):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"pump_status":pump_status,
		"airpump_status":airpump_status
	}
	rc = HP.http_post(base_url+thing_name_equipment,payload)
	return rc

def dweet_update_feeding(feed_type,feed_amount):
	payload = {
		"logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
		"feed_type": feed_type,
		"feed_amount": feed_amount
	}
	rc = HP.http_post(base_url+thing_name_feeding,payload)
	return rc
