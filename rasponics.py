#!/usr/bin/python
import datetime
import time
import logging

import Adafruit_DHT as DHT
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

import fish_feeder as FEEDER
import lcd_display as DISPLAY
import log_to_google as GLOG

#
# Setup logging
#
logging.basicConfig(filename='/var/log/rasponics.log',level=logging.INFO,format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %I:%M:%S %p')
logging.info('Rasponics v1.0.0 starting')
DISPLAY.update(0, 'Rasponics v1.0.0','(c) Burketech')

# Define the internal temp/humidity sensor
sensor = DHT.DHT22
pin = 23

# Feeder settings

# Start day
START_DATE = datetime.date(2016,7,20)

# Number of fish to feed
FISH_COUNT = 50

# Feedings 
FEED_TIMES = [ '0:00', '4:00', '8:00', '12:00', '16:00', '20:00' ]
#FEED_TIMES = [ '0:00', '4:00', '8:00', '18:15', '17:58', '20:00' ]
FEED_PER_DAY = len(FEED_TIMES)

# Initialize the GPIO
Relay1=17
Relay2=18
Relay3=27
Relay4=22 # Feeder

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering

GPIO.setup(Relay4, GPIO.OUT)

# Prevent a feeding at start time, if we happen to restart on a feed time
last_feeding = time.strftime('%H:%M',time.localtime(time.time()))

# Initialize our feeding data 
(day_number,feed_type,feed_today,feed_per_feeding,feed_duration) = FEEDER.get_feeding(START_DATE,FISH_COUNT,FEED_PER_DAY)

while True:
	DISPLAY.update(1, "Day %d Feeding" % day_number, "%dg of %s" % (feed_today, feed_type))

	nowtime = time.strftime('%H:%M',time.localtime(time.time()))
	#nowtime = '0:00'
	next_feeding = FEEDER.next_feed_time(FEED_TIMES,nowtime)

	if next_feeding == last_feeding :
		DISPLAY.update(2,'Just fed the fish',"%dg of %s" % (feed_per_feeding, feed_type))
	else:
		DISPLAY.update(2,"Time %11s" % nowtime, "Next Feed %6s" % next_feeding)

	if nowtime == next_feeding and next_feeding != last_feeding :

		#
		# Time to feed the fish
		#

		(day_number,feed_type,feed_today,feed_per_feeding,feed_duration) = FEEDER.get_feeding(START_DATE,FISH_COUNT,FEED_PER_DAY)

		DISPLAY.show_now("Feeding %d secs" % feed_duration, "%.1fg of %s" % (feed_per_feeding, feed_type))

		#
		# Turn on the fish feeder for the calculated time
		#	
		FEEDER.feed_fish(feed_duration, feed_per_feeding, feed_type, Relay4)	
		GLOG.log_to_google(datetime.datetime.now(), feed_type, "%.1f" % feed_per_feeding)

		last_feeding = nowtime

	# Read the air temperature and humidity from DHT22

	# If seeing a lot of failures, switch to the read_retry method
	humidity, temperature = DHT.read(sensor,pin)
	#humidity, temperature = DHT.read_retry(sensor,pin)

	if humidity is not None and temperature is not None:
		temperature = temperature * 9/5.0 + 32
		DISPLAY.update(3, 'Air Temp {0:6.1f}F'.format(temperature), 'Humidity {0:6.1f}%'.format(humidity))

	#
	# Display rotating message on LCD
	#
	DISPLAY.show_next()
	
	time.sleep(2)

#	for sensor in W1ThermSensor.get_available_sensors():
#		print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))

