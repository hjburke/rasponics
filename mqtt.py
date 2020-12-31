"""mqtt.py

This module provides data logging and commands to/from an MQTT message broker.

"""

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import json
import config
import logging

def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT Server RC="+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(config.mqtt_base_topic+"#")
    # Add callbacks for the specific commands
    for cb in userdata:
        client.message_callback_add(config.mqtt_base_topic+cb[0], cb[1])

def on_disconnect(client, userdata, flags, rc):
    logging.info("Disconnected to MQTT Server RC="+str(rc))

def init(callbacks):
    global mc
    mc = mqtt.Client(client_id="rasponics", userdata=callbacks)
    mc.username_pw_set(config.mqtt_user,config.mqtt_pass)
    mc.on_connect = on_connect
    mc.on_disconnect = on_disconnect
    mc.connect(config.mqtt_host)
    return mc

def publish_status(air_temp,humidity,tank_top_temp,tank_bottom_temp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status,ph):
    payload = {
        "time": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "air_temp": round(air_temp,1),
        "humidity": humidity,
        "tank_top_temp": round(tank_top_temp,1),
        "tank_bottom_temp": round(tank_bottom_temp,1),
        "ph": round(ph,1),
        "growbed_cycle_duration": GB_duration,
        "growbed_cycle_direction": GB_direction,
        "growbed_cycle_transition_time": time.strftime("%Y-%m-%d %H:%M",time.localtime(GB_last_transition)),
        "pump": "ON" if pump_status==True else "OFF",
        "airpump": "ON" if airpump_status==True else "OFF"
    }
    if 'mc' in globals():
        return mc.publish(config.mqtt_base_topic+"state", payload=json.dumps(payload))
    else:
        return

def publish_feeding(tank,feed_type,feed_amount):
    payload = {
        "time": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "tank": tank,
        "feed_type": feed_type,
        "feed_amount": "{0:3.1f}".format(feed_amount)
    }
    return mc.publish(config.mqtt_base_topic+"feeding", payload=json.dumps(payload))

def publish_growbed(GB_duration,GB_direction,GB_last_transition):
    payload = {
        "time": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "growbed_cycle_duration": GB_duration,
        "growbed_cycle_direction": GB_direction,
        "growbed_cycle_transition_time": time.strftime("%Y-%m-%d %H:%M",time.localtime(GB_last_transition))
    }
    return mc.publish(config.mqtt_base_topic+"growbed", payload=json.dumps(payload))

def publish_pump(status):
    payload = {
        "time": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "status": "ON" if status==True else "OFF"
    }
    return mc.publish(config.mqtt_base_topic+"pump", payload=json.dumps(payload))

def publish_airpump(status):
    payload = {
        "time": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
        "status": "ON" if status==True else "OFF"
    }
    return mc.publish(config.mqtt_base_topic+"airpump", payload=json.dumps(payload))

def publish_pump_cmd(cmd):
    return mc.publish(config.mqtt_base_topic+"pump/cmd", cmd)

def publish_airpump_cmd(cmd):
    return mc.publish(config.mqtt_base_topic+"airpump/cmd", cmd)

def publish_feeder_cmd(tank,cmd):
    return mc.publish(config.mqtt_base_topic+"feeder/%s/cmd" % tank, cmd)