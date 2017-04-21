"""lcd_display.py

This module provides a rotating display on the Adafruit Pi Plate.
Uses the Adafruit CharLCD library (https://github.com/adafruit/Adafruit_Python_CharLCD).
In addition to writing to the LCD, it also writes a matching txt file into /dev/shm/lcd.txt.
Also provides access to check the status of the 5 buttons on the display.

Usage:

update store the lines of text into one of the buffers.
show_next updates the display with the next message in the buffer.
show_now will immediately display the supplied text.
is_<button>_pressed will return True if the referenced button (select,up,down,left,right) is pressed.

ToDo:

Continue to modify to support different dimension LCD's, right now some operations are limited to 2 lines.

"""

import Adafruit_CharLCD as LCD
import threading

# Constants
LCD_WIDTH=16
LCD_HEIGHT=2
NUM_BUFFERS=6

# Update in process flag
#uip = False

lock = threading.Lock()

# LCD Message number
msgid = 0

LCDMessage = [['' for j in range(LCD_HEIGHT)] for i in range(NUM_BUFFERS)]

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

#
# Update the given slot in the message buffer, limiting each row to the defined LCD width.
# Message slots start at 0.
#
def update(slot,*lines):
    if slot<NUM_BUFFERS:
        row=0
        for line in lines:
            if row<LCD_HEIGHT:
                LCDMessage[slot][row] = '{:{width}.{width}}'.format(line,width=LCD_WIDTH)
                row += 1

#
# Display message on LCD instantly
#
def show_now(line1,line2):
    global uip
    # If an update is already in process, bomb out its not that important!
    #if uip is False:
    lock.acquire()
    try:
        #uip = True
        tmpMsg = line1 + "\n" + line2
        lcd.clear() 
        lcd.message(tmpMsg)
        _write_lcd_file(line1,line2)
        #uip = False
    finally:
        lock.release()

#
# Display next rotating message on LCD
#
def show_next():
    global msgid
    show_now(LCDMessage[msgid][0],LCDMessage[msgid][1])
    # Move to next message
    msgid += 1
    if msgid == len(LCDMessage): msgid=0

#
# Write the current LCD diplay contents to a file, for future web display
#
def _write_lcd_file(msg1,msg2):
    f = open("/dev/shm/lcd.txt","w")
    f.write('******************\n')
    f.write('*%s*\n' % msg1)
    f.write('*%s*\n' % msg2)
    f.write('******************\n')
    f.close()

#
# Handle button presses
#
def is_select_pressed():
    return lcd.is_pressed(LCD.SELECT)

def is_up_pressed():
    return lcd.is_pressed(LCD.UP)

def is_down_pressed():
    return lcd.is_pressed(LCD.DOWN)

def is_left_pressed():
    return lcd.is_pressed(LCD.LEFT)

def is_right_pressed():
    return lcd.is_pressed(LCD.RIGHT)
