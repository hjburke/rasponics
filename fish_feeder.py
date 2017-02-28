#
# Calculate how long the fish feeder should run, based
# on our feeding schedule, the number of fish and how
# many times each day we want to feed them.
#
import datetime
import time
import logging

import RPi.GPIO as GPIO

import config

# Fish feed rates per day
# Based on table at https://lakewaytilapia.com/Tilapia-Feeding-Guide.php
# This is grams per 100 tilapia

# 28 days of AquaMax Fingerling Starter 300 1/16 sinking pellet
FEED_AMOUNT_AM300 = [
38, 39, 41, 43, 44, 46, 48, 50, 52, 54, 56, 58, 61, 63,
65, 68, 71, 74, 77, 80, 83, 86, 90, 93, 97, 101, 105, 109
]

# 24 days of AquaMax Grower 400 3/32 sinking pellet
FEED_AMOUNT_AM400 = [
85, 88, 90, 93, 96, 99, 102, 105, 108, 111, 114, 118, 121,
125, 129, 133, 136, 141, 145, 149, 154, 158, 163, 168
]

# 142 days of AquaMax Dense 4000 3/16 floating pellet
FEED_AMOUNT_AM4000 = [
85, 86, 88, 89, 90, 92, 93, 94, 96, 97, 99, 100, 102, 103,
105, 106, 108, 110, 111, 113, 115, 116, 118, 120, 122, 123,
125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, 148,
150, 152, 154, 157, 159, 161, 164, 166, 169, 171, 174, 176,
179, 182, 185, 187, 190, 193, 196, 199, 202, 205, 208, 207,
210, 213, 216, 220, 223, 226, 230, 233, 237, 240, 244, 247,
251, 255, 259, 263, 266, 270, 275, 279, 283, 287, 291, 296,
300, 305, 309, 314, 319, 323, 328, 333, 338, 343, 348, 354,
359, 364, 370, 375, 381, 387, 392, 398, 404, 410, 416, 423,
429, 436, 442, 449, 455, 462, 469, 476, 483, 491, 498, 505,
513, 521, 529, 536, 544, 553, 561, 569, 578, 587, 595, 604,
613, 623, 632, 641, 651, 661, 671, 681
]

FEED_AMOUNTS = FEED_AMOUNT_AM300 + FEED_AMOUNT_AM400 + FEED_AMOUNT_AM4000

FEED_DAYS = len(FEED_AMOUNTS)

#
# Calculate then the next feed time is, based on the feeding schedule and the current time.
#
def next_feed_time(feed_times, nowtime):
    now = time.strptime(nowtime,'%H:%M')

    for i in range(len(feed_times)):
        t1 = time.strptime(feed_times[i], '%H:%M')

        if t1 == now:
            next_feed = feed_times[i]   # It is exactly the next feed time
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

# Calculate how long the fish feeder should run, based
# on our feeding schedule, the number of fish and how
# many times each day we want to feed them.
#
# Inputs
#   Start Day
#   Number of Fish
#   Feeds per Day
# Outputs
#   Day number
#   Feed type
#   Total feed today (grams)
#   Feed per feeding (grams)
#   Feed duration (seconds)

def get_feeding(start_date, number_of_fish, feeds_per_day):

    # What feeding day are we on
    today = datetime.date.today()
    day_number = (today - start_date).days

    # What type of feed should we be using
    # Based on Purina AquaMax
    if day_number < len(FEED_AMOUNT_AM300) :
        feed_type = "AM300"
    elif len(FEED_AMOUNT_AM300) <= day_number < len(FEED_AMOUNT_AM300)+len(FEED_AMOUNT_AM400) :
        feed_type = "AM400"
    elif len(FEED_AMOUNT_AM300)+len(FEED_AMOUNT_AM400) <= day_number :
        feed_type = "AM4000"

    # Calculate total feed today, if beyond the harvest date, use the harvest date feed amount
    if day_number < FEED_DAYS :
        feed_today = float(FEED_AMOUNTS[day_number]) * number_of_fish / 100
    else:
        feed_today = float(FEED_AMOUNTS[FEED_DAYS-1]) * number_of_fish / 100

    # How much should we feed in each feeding, in grams
    feed_per_feeding = feed_today / feeds_per_day

    # How long should the fish feeder run for a given feeding
    feed_duration = feed_per_feeding / config.FEED_RATES[feed_type]

    return (day_number,feed_type,feed_today,feed_per_feeding,feed_duration)

def feed_fish(feed_duration, feed_amount, feed_type, feeder_gpio):

    logging.info('Feeding %.1fg of %s over %dseconds',feed_amount,feed_type,feed_duration)

    GPIO.output(feeder_gpio,True)
    time.sleep(feed_duration)
    GPIO.output(feeder_gpio,False)

    return()
