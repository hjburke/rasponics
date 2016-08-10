import Adafruit_CharLCD as LCD

# LCD Message number
msgid = 0
LCDMessageLine1 = ['','','','','']
LCDMessageLine2 = ['','','','','']

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

def update(slot,line1,line2):
    LCDMessageLine1[slot] = '%-16s' % line1
    LCDMessageLine2[slot] = '%-16s' % line2

#
# Display message on LCD instantly
#
def show_now(line1,line2):
    tmpMsg = line1 + "\n" + line2
    lcd.clear() 
    lcd.message(tmpMsg)
    write_lcd_file(line1,line2)

#
# Display next rotating message on LCD
#
def show_next():
    global msgid
    show_now(LCDMessageLine1[msgid],LCDMessageLine2[msgid])
    # Move to next message
    msgid += 1
    if msgid == len(LCDMessageLine1): msgid=0

def write_lcd_file(msg1,msg2):
    # Write LCD display contents to file, for future web display
    f = open("/dev/shm/lcd.txt","w")
    f.write('******************\n')
    f.write('*%s*\n' % msg1)
    f.write('*%s*\n' % msg2)
    f.write('******************\n')
    f.close()

