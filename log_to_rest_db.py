"""log_to_rest_db.py

This module provides data logging to a database via a REST CRUD API..

"""

import time
#import json
#import requests
import config
#import threading
import http_post as HP
import logging

db_status_log_table = 'rasponics_status_log'
db_feeding_log_table = 'rasponics_feeding_log'

#lock = threading.Lock()

def update_status_log(air_temp,humidity,tank_top_temp,tank_bottom_temp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status):
    logging.info("update_status_log: Enter")

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

    #rc = send_to_db(db_status_log_table, payload)
    rc = HP.http_post(config.api_base+db_status_log_table, payload)
    logging.info("update_status_log: Exit")
    return rc

def update_feeding_log(feed_type,feed_amount):
    logging.info("update_feeding_log: Enter")
    payload = {
        "logtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "feed_type":feed_type,
        "feed_amount":'{0:3.1f}'.format(feed_amount)
    }

    #rc = send_to_db(db_feeding_log_table, payload)
    rc = HP.http_post(config.api_base+db_feeding_log_table, payload)
    logging.info("update_feeding_log: Exit")
    return rc

#def send_to_db(table_name, payload):
#    lock.acquire()
#    try:
#        print "send_to_db: about to post {}".format(payload)
#        response = requests.post(config.api_base+table_name, data=json.dumps(payload), headers={'content-type':'application/json'})
#        rc = response.status_code
#    except Exception as e:
#	print "send_to_db: Error sending to rest API"
#	rc =500
#    finally:
#        lock.release()
#
#    return rc
