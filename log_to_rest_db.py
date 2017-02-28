"""log_to_rest_db.py

This module provides data logging to a database via a REST CRUD API..

"""

import time
import json
import requests

import config

db_status_log_table = 'rasponics_status_log'
db_feeding_log_table = 'rasponics_feeding_log'

def update_status_log(air_temp,humidity,tank_top_temp,tank_bottom_temp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status):

    payload = {
        "logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "air_temp":air_temp,
        "humidity":humidity,
        "tank_top_temp":tank_top_temp,
        "tank_bottom_temp":tank_bottom_temp,
        "growbed_cycle_duration":GB_duration,
        "growbed_cycle_direction":GB_direction,
        "growbed_cycle_transition_time":time.strftime("%Y-%m-%d %H:%M",time.localtime(GB_last_transition)),
        "pump_status":pump_status,
        "airpump_status":airpump_status
    }

    try:
        response = requests.post(config.api_base+db_status_log_table, data=json.dumps(payload), headers={'content-type':'application/json'})
    except:
        return 500

    return response.status_code

def update_feeding_log(feed_type,feed_amount):

    payload = {
        "logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "feed_type":feed_type,
        "feed_amount":'{0:3.1f}'.format(feed_amount)
    }

    try:
        response = requests.post(config.api_base+db_feeding_log_table, data=json.dumps(payload), headers={'content-type':'application/json'})
    except:
        return 500

    return response.status_code
