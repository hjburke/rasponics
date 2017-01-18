#!/usr/bin/python
import datetime
import time
import logging
import threading

import Adafruit_DHT as DHT
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

import fish_feeder as FEEDER
import lcd_display as DISPLAY
import log_to_google as GLOG

# Workaround for a Python threading bug with strptime function
throwaway = datetime.datetime.strptime('20110101','%Y%m%d')

LCD_REFRESH = 5		# how frequently the LCD display is updated
TEMP_REFRESH = 5*60	# how frequently the temperatures are read and recorded

#
# Setup logging
#
logging.basicConfig(filename='/var/log/rasponics.log',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %I:%M:%S %p')
logging.info('Rasponics v1.0.0 starting')
DISPLAY.update(0, 'Rasponics v1.0.0','(c) Burketech')

# Define the internal temp/humidity sensor
sensor = DHT.DHT22
pin = 23

# Define the external temp sensors
#TANK_SENSOR = "00042b35feff"
SUMP_SENSOR = "00042b321bff"
TANK_SENSOR = "00042e07f5ff"

# Feeder settings

# Start day
START_DATE = datetime.date(2016,7,20)

# Number of fish to feed
FISH_COUNT = 25

# Feedings 
FEED_TIMES = [ '00:00', '04:00', '08:00', '12:00', '16:00', '20:00' ]
#FEED_TIMES = [ '0:00', '4:00', '8:00', '18:15', '17:58', '20:00' ]
FEED_PER_DAY = len(FEED_TIMES)

# Initialize the GPIO
Relay1=17
Relay2=18
Relay3=27
Relay4=22 # Feeder
#water_sensor = 24


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering

GPIO.setup(Relay4, GPIO.OUT)
GPIO.output(Relay4,False)

#GPIO.setup(water_sensor, GPIO.IN)
#grow_bed_waterlevel = GPIO.input(water_sensor)

# Prevent a feeding at start time, if we happen to restart on a feed time
last_feeding = time.strftime('%H:%M',time.localtime(time.time()))

#
# A repeating thread to read the temp probes every n seconds
#
def get_temps():
    # Read the air temperature and humidity from DHT22

    # If seeing a lot of failures, switch to the read_retry method
    #humidity, airtemp = DHT.read(sensor,pin)
    humidity, airtemp = DHT.read_retry(sensor,pin)

    if humidity is not None and airtemp is not None:
        airtemp = airtemp * 9/5.0 + 32
        DISPLAY.update(3, 'Air Temp {0:6.1f}F'.format(airtemp), 'Humidity {0:6.1f}%'.format(humidity))
        #logging.info("Air Temp %.1fF Humidity %0.1f" % (airtemp, humidity))
    else:
        airtemp = 0
        humidity = 0
        logging.warning("Failed to fetch air temperature or humidity")

    try:
        tanktemp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, TANK_SENSOR).get_temperature(W1ThermSensor.DEGREES_F)
    except Exception:
        tanktemp = 0
        logging.warning("Failed to fetch tank temperature")

    try:
        sumptemp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, SUMP_SENSOR).get_temperature(W1ThermSensor.DEGREES_F)
    except Exception:
        sumptemp = 0
        logging.warning("Failed to fetch sump temperature")

    DISPLAY.update(4, 'Tank Temp {0:5.1f}F'.format(tanktemp), 'Sump Temp {0:5.1f}F'.format(sumptemp))

    # Record the temp/humidity values in Goggle Sheets
    GLOG.log_temps_to_google(datetime.datetime.now(), "%.1f" % airtemp, "%.1f" % humidity, "%.1f" % tanktemp, "%.1f" % sumptemp)

    # Start threading this every n minutes
    threading.Timer(TEMP_REFRESH, get_temps).start()

threading.Thread(target=get_temps).start()

#
# A repeating thread to refresh the LCD display every n seconds
#
def refresh_display():
    DISPLAY.show_next()
    threading.Timer(LCD_REFRESH, refresh_display).start()

threading.Thread(target=refresh_display).start()

#
# MAIN
#
while True:
    (day_number,feed_type,feed_today,feed_per_feeding,feed_duration) = FEEDER.get_feeding(START_DATE,FISH_COUNT,FEED_PER_DAY)
 
    #logging.info("Feeding %.1fg of %s for %.1fsec" % (feed_per_feeding,feed_type,feed_duration))
    
    DISPLAY.update(1, "Day %d Feeding" % day_number, "%dg of %s" % (feed_today, feed_type))

    nowtime = time.strftime('%H:%M',time.localtime(time.time()))
    #nowtime = '07:00'
    next_feeding = FEEDER.next_feed_time(FEED_TIMES,nowtime)

    if next_feeding == last_feeding :
        DISPLAY.update(2,'Just fed the fish',"%dg of %s" % (feed_per_feeding, feed_type))
    else:
        DISPLAY.update(2,"Time %11s" % nowtime, "Next Feed %6s" % next_feeding)

    if nowtime == next_feeding and next_feeding != last_feeding :

        #
        # Time to feed the fish
        #
        DISPLAY.show_now("Feeding %d secs" % feed_duration, "%.1fg of %s" % (feed_per_feeding, feed_type))

        #
        # Turn on the fish feeder for the calculated time
        #
        FEEDER.feed_fish(feed_duration, feed_per_feeding, feed_type, Relay4)
        GLOG.log_feeding_to_google(datetime.datetime.now(), feed_type, "%.1f" % feed_per_feeding)

        last_feeding = nowtime

    if DISPLAY.is_select_pressed():
        DISPLAY.show_now("Feeding %d secs" % feed_duration, "%.1fg of %s" % (feed_per_feeding, feed_type))
        FEEDER.feed_fish(feed_duration, feed_per_feeding, feed_type, Relay4)
        GLOG.log_feeding_to_google(datetime.datetime.now(), feed_type, "%.1f" % feed_per_feeding)

    #
    # Check if the grow bed water level has changed
    #
#    curr_waterlevel = GPIO.input(water_sensor)
#    if curr_waterlevel != grow_bed_waterlevel:
#        grow_bed_waterlevel = curr_waterlevel
#	direction = "Flooding" if curr_waterlevel == 0 else "Draining"
#        logging.info("Growbed %s" % direction)
