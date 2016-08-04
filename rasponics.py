import datetime
import time

import Adafruit_DHT as DHT
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

import fish_feeder

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
FEED_PER_DAY = len(FEED_TIMES)

# Initialize the GPIO
Relay1=17
Relay2=18
Relay3=27
Relay4=22 # Feeder

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Use board pin numbering

GPIO.setup(Relay4, GPIO.OUT)

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

def next_feed_time(feed_times, nowtime):
    now = time.strptime(nowtime,'%H:%M')

    for i in range(len(feed_times)):
        t1 = time.strptime(feed_times[i], '%H:%M')

        if t1 == now:
            next_feed = feed_times[i]	# It is exactly the next feed time
            break
        # If we are > the last time, then the next time is the first time
        elif i == len(feed_times)-1:
            next_feed = feed_times[0]
            break
        else:
            t2 = time.strptime(feed_times[i+1], '%H:%M')
            if now >= t1 and now < t2:
                next_feed = feed_times[i+1]
                break

    return next_feed

# Prevent a feeding at start time, if we happen to restart on a feed time
last_feeding = time.strftime('%H:%M',time.localtime(time.time()))

# Initialize our feeding data 
(day_number,feed_type,feed_today,feed_per_feeding,feed_duration) = fish_feeder.get_feeding(START_DATE,FISH_COUNT,FEED_PER_DAY)

# LCD Message number
n = 0
LCDMessage = ['Rasponics v1.0.0\n(c) Burketech','','','']

while True:
	LCDMessage[1] = "Day %d Feeding\n%dg of %s" % (day_number, feed_today, feed_type)

	nowtime = time.strftime('%H:%M',time.localtime(time.time()))
	#nowtime = '0:00'
	next_feeding = next_feed_time(FEED_TIMES,nowtime)

	if next_feeding == last_feeding :
		LCDMessage[2] = "Just fed the fish\n%d grams of %s" % (feed_per_feeding, feed_type)
	else:
		LCDMessage[2] = "Time %s\nNext Feed %s" % (nowtime, next_feeding)

	if nowtime == next_feeding and next_feeding != last_feeding :
		(day_number,feed_type,feed_today,feed_per_feeding,feed_duration) = fish_feeder.get_feeding(START_DATE,FISH_COUNT,FEED_PER_DAY)

		tmpMsg = "Feeding %i secs\n%dg of %s" % (feed_duration, feed_per_feeding, feed_type)
	
		lcd.clear()
		lcd.message(tmpMsg)
		print tmpMsg
		
		GPIO.output(Relay4,True)
		time.sleep(feed_duration)
		GPIO.output(Relay4,False)

		last_feeding = nowtime

	# Read the air temperature and humidity from DHT22

	# If seeing a lot of failures, switch to the read_retry method
	humidity, temperature = DHT.read(sensor,pin)
	#humidity, temperature = DHT.read_retry(sensor,pin)

	if humidity is not None and temperature is not None:
		temperature = temperature * 9/5.0 + 32
		LCDMessage[3] = ('Air Temp={0:0.1f}F\nHumidity={1:0.1f}%'.format(temperature, humidity))

	# Display rotating message on LCD
	lcd.clear()
	lcd.message(LCDMessage[n])
	print LCDMessage[n]
	n = n + 1
	if n == len(LCDMessage): n=0
	
	time.sleep(2)

#	for sensor in W1ThermSensor.get_available_sensors():
#		print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))

