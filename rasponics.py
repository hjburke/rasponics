#!/usr/bin/python
import datetime
import time
import logging
import threading

import Adafruit_DHT as DHT
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

import config
import hwconfig as HW
import fish_feeder as FEEDER
import lcd_display as DISPLAY
import log_to_google as GLOG
import log_to_dweet as DLOG
import log_to_rest_db as RLOG
import log_to_thingspeak as TSLOG

# Workaround for a Python threading bug with strptime function
throwaway = datetime.datetime.strptime('20110101','%Y%m%d')

# Record startup time
startup_time = time.time()

#
# Setup logging
#
logging.basicConfig(filename='/var/log/rasponics.log',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %I:%M:%S %p')
logging.info('Rasponics v1.0.0 starting')
DISPLAY.update(0, 'Rasponics v1.1.0','(c) Burketech')

# Initialize the GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering

GPIO.setup(HW.tank1_fish_feeder, GPIO.OUT)
GPIO.setup(HW.tank2_fish_feeder, GPIO.OUT)
GPIO.setup(HW.air_pump, GPIO.OUT)
GPIO.setup(HW.water_pump, GPIO.OUT)
GPIO.output(HW.tank1_fish_feeder,False)
GPIO.output(HW.tank2_fish_feeder,False)

GPIO.setup(HW.gb_water_sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP )

feedings = []
# Prevent a feeding at start time, if we happen to restart on a feed time
feedings.append({"last_feeding" : time.strftime('%H:%M',time.localtime(startup_time))})
feedings.append({"last_feeding" : time.strftime('%H:%M',time.localtime(startup_time))})

# Setup the timers for the rising and falling of the growbed
GB_time_rising = startup_time
GB_time_falling = startup_time
GB_duration = 0
GB_direction = ' '
GB_last_transition = startup_time

# Setup the variables to store temps
airtemp = 0
humidity = 0
tanktoptemp = 0
tankbtmtemp = 0

# Equipment status
pump_status = 1
airpump_status = 1

#
# Handler for growbed water level changes
#
def GB_change(channel):
    global GB_time_rising, GB_time_falling, GB_duration, GB_direction, GB_last_transition

    nowtime = time.time()

    x = GPIO.input(channel)
    if x:
        GB_direction = "v"
        GB_duration = int(nowtime - GB_time_falling)
        GB_time_falling = nowtime
    	logging.info('Growbed change detected - falling')
    else:
        GB_direction = "^"
        GB_duration = int(nowtime - GB_time_rising)
        GB_time_rising = nowtime
    	logging.info('Growbed change detected - rising')

    GB_last_transition = nowtime

    DISPLAY.update(5, 'GB Cycle {} {d[0]:2}:{d[1]:02}'.format(GB_direction, d=divmod(GB_duration,60)), '{}'.format(time.strftime("%d %b %H:%M:%S",time.localtime(nowtime))))

    # Realtime update of growbed change to DWEET
    DLOG.dweet_update_growbed(GB_duration, GB_direction, nowtime)

GPIO.add_event_detect(HW.gb_water_sensor, GPIO.BOTH, callback=GB_change, bouncetime=200)

#
# A repeating thread to read the temp probes every n seconds
#
def get_temps():
    global airtemp,humidity,tanktoptemp,tankbtmtemp
    
    # Read the air temperature and humidity from DHT22

    # If seeing a lot of failures, switch to the read_retry method
    #humidity, airtemp = DHT.read(DHT.DHT22,HW.dht22_sensor)
    humidity, airtemp = DHT.read_retry(DHT.DHT22,HW.dht22_sensor)

    if humidity is not None and airtemp is not None:
        airtemp = airtemp * 9/5.0 + 32
        DISPLAY.update(3, 'Air Temp {0:6.1f}F'.format(airtemp), 'Humidity {0:6.1f}%'.format(humidity))
    else:
        airtemp = 0
        humidity = 0
        logging.warning("Failed to fetch air temperature or humidity")

    try:
        tanktoptemp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, HW.tank_top_sensor).get_temperature(W1ThermSensor.DEGREES_F)
    except Exception:
        tanktoptemp = 0
        logging.warning("Failed to fetch tank top temperature")

    try:
        tankbtmtemp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, HW.tank_btm_sensor).get_temperature(W1ThermSensor.DEGREES_F)
    except Exception:
        tankbtmtemp = 0
        logging.warning("Failed to fetch tank bottom temperature")

    #try:
    #    sumptemp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, SUMP_SENSOR).get_temperature(W1ThermSensor.DEGREES_F)
    #except Exception:
    #    sumptemp = 0
    #    logging.warning("Failed to fetch sump temperature")

    DISPLAY.update(4, 'Tank Top  {0:5.1f}F'.format(tanktoptemp), 'Tank Btm  {0:5.1f}F'.format(tankbtmtemp))

    # Realtime update of temps to DWEET
    DLOG.dweet_update_temps(airtemp, humidity, tanktoptemp, tankbtmtemp)

    # Start threading this every n seconds
    threading.Timer(config.TEMP_REFRESH, get_temps).start()

threading.Thread(target=get_temps).start()

#
# A repeating thread to refresh the LCD display every n seconds
#
def refresh_display():
    DISPLAY.show_next()
    threading.Timer(config.LCD_REFRESH, refresh_display).start()

threading.Thread(target=refresh_display).start()

#
# A repeating thread to update the equipment status
#
def update_equipment():
    global pump_status, airpump_status

    # Because we are wired for failsafe operation, pumps are on
    # when the GPIO's are LOW.
    pump_status = not GPIO.input(HW.water_pump)
    airpump_status = not GPIO.input(HW.air_pump)

    # Realtime update of equipment to DWEET
    delog = threading.Thread(target=DLOG.dweet_update_equipment, args=(pump_status,airpump_status))
    delog.start()

    threading.Timer(config.EQUIP_REFRESH, update_equipment).start()

threading.Thread(target=update_equipment).start()

#
# A repeating thread to log status to DB (via REST API) and Google Sheets
#
def log_status():
    # Dont log until we have at least the air temp captured
    if (airtemp != 0):
        RLOG.update_status_log(airtemp,humidity,tanktoptemp,tankbtmtemp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status)
        GLOG.update_status_log(airtemp,humidity,tanktoptemp,tankbtmtemp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status)
        TSLOG.update_status_log(airtemp,humidity,tanktoptemp,tankbtmtemp,pump_status,airpump_status)

    threading.Timer(config.LOGGING_REFRESH, log_status).start()

threading.Thread(target=log_status).start()

#
# MAIN
#
while True:
    (feedings[0]["day_number"],feedings[0]["feed_type"],feedings[0]["feed_today"],feedings[0]["feed_per_feeding"],feedings[0]["feed_duration"]) = FEEDER.get_feeding(config.TANK1_START_DATE,config.TANK1_FISH_COUNT,len(config.TANK1_FEED_TIMES),config.TANK1_FEED_RATES)
    (feedings[1]["day_number"],feedings[1]["feed_type"],feedings[1]["feed_today"],feedings[1]["feed_per_feeding"],feedings[1]["feed_duration"]) = FEEDER.get_feeding(config.TANK2_START_DATE,config.TANK2_FISH_COUNT,len(config.TANK2_FEED_TIMES),config.TANK2_FEED_RATES)

    nowtime = time.strftime('%H:%M',time.localtime(time.time()))
    feedings[0]["next_feeding"] = FEEDER.next_feed_time(config.TANK1_FEED_TIMES,nowtime)
    feedings[1]["next_feeding"] = FEEDER.next_feed_time(config.TANK2_FEED_TIMES,nowtime)

    DISPLAY.update(1, "Day %d Feeding" % feedings[0]["day_number"], "%dg of %s" % (feedings[0]["feed_today"], feedings[0]["feed_type"]))

    if feedings[0]["next_feeding"] == feedings[0]["last_feeding"] :
        DISPLAY.update(2,'Just fed the fish',"%dg of %s" % (feedings[0]["feed_per_feeding"], feedings[0]["feed_type"]))
    else:
        DISPLAY.update(2,"Time %11s" % nowtime, "Next Feed %6s" % feedings[0]["next_feeding"])

    # MAIN TANK

    if config.TANK1_FISH_COUNT > 0 and nowtime == feedings[0]["next_feeding"] and feedings[0]["next_feeding"] != feedings[0]["last_feeding"] :

        #
        # Time to feed the fish
        #
        DISPLAY.show_now("Feeding %d secs" % feedings[0]["feed_duration"], "%.1fg of %s" % (feedings[0]["feed_per_feeding"], feedings[0]["feed_type"]))

        #
        # Turn on the fish feeder for the calculated time
        #
        FEEDER.feed_fish(feedings[0]["feed_duration"], feedings[0]["feed_per_feeding"], feedings[0]["feed_type"], HW.tank1_fish_feeder)
        DLOG.dweet_update_feeding(feedings[0]["feed_type"], feedings[0]["feed_per_feeding"])
        GLOG.update_feeding_log(feedings[0]["feed_type"], feedings[0]["feed_per_feeding"])
	RLOG.update_feeding_log(feedings[0]["feed_type"], feedings[0]["feed_per_feeding"])

        feedings[0]["last_feeding"] = nowtime

    # NURSERY TANK

    if config.TANK2_FISH_COUNT > 0 and nowtime == feedings[1]["next_feeding"] and feedings[1]["next_feeding"] != feedings[1]["last_feeding"] :

        #
        # Time to feed the fish
        #
        DISPLAY.show_now("Feeding %d secs" % feedings[1]["feed_duration"], "%.1fg of %s" % (feedings[1]["feed_per_feeding"], feedings[1]["feed_type"]))

        #
        # Turn on the fish feeder for the calculated time
        #
        FEEDER.feed_fish(feedings[1]["feed_duration"], feedings[1]["feed_per_feeding"], feedings[1]["feed_type"], HW.tank2_fish_feeder)
        DLOG.dweet_update_feeding(feedings[1]["feed_type"], feedings[1]["feed_per_feeding"])
        GLOG.update_feeding_log(feedings[1]["feed_type"], feedings[1]["feed_per_feeding"])
        RLOG.update_feeding_log(feedings[1]["feed_type"], feedings[1]["feed_per_feeding"])

        feedings[1]["last_feeding"] = nowtime

    #
    # Check for key presses
    #

    if DISPLAY.is_select_pressed():
        logging.info("Select button pressed")
        DISPLAY.show_now("Feeding %d secs" % feedings[0]["feed_duration"], "%.1fg of %s" % (feedings[0]["feed_per_feeding"], feedings[0]["feed_type"]))
        FEEDER.feed_fish(feedings[0]["feed_duration"], feedings[0]["feed_per_feeding"], feedings[0]["feed_type"], HW.tank1_fish_feeder)
        DLOG.dweet_update_feeding(feedings[0]["feed_type"], feedings[0]["feed_per_feeding"])
        GLOG.update_feeding_log(feedings[0]["feed_type"], feedings[0]["feed_per_feeding"])
	RLOG.update_feeding_log(feedings[0]["feed_type"], feedings[0]["feed_per_feeding"])

    if DISPLAY.is_up_pressed():
        logging.info("Up button pressed")
        GPIO.output(HW.water_pump,False)
	delog = threading.Thread(target=DLOG.dweet_update_equipment, args=(False if GPIO.input(HW.water_pump) else True,False if GPIO.input(HW.air_pump) else True))
	delog.start()

    if DISPLAY.is_down_pressed():
        logging.info("Down button pressed")
        GPIO.output(HW.water_pump,True)
	delog = threading.Thread(target=DLOG.dweet_update_equipment, args=(False if GPIO.input(HW.water_pump) else True,False if GPIO.input(HW.air_pump) else True))
	delog.start()

    if DISPLAY.is_left_pressed():
        logging.info("Left button pressed")
        GPIO.output(HW.air_pump,True)
	delog = threading.Thread(target=DLOG.dweet_update_equipment, args=(False if GPIO.input(HW.water_pump) else True,False if GPIO.input(HW.air_pump) else True))
	delog.start()

    if DISPLAY.is_right_pressed():
        logging.info("Right button pressed")
        GPIO.output(HW.air_pump,False)
	delog = threading.Thread(target=DLOG.dweet_update_equipment, args=(False if GPIO.input(HW.water_pump) else True,False if GPIO.input(HW.air_pump) else True))
	delog.start()
