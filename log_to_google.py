import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

GDOCS_OAUTH_JSON = '/home/hburke/rasponics/5b689121080b.json'
GDOCS_SPREADSHEET_NAME = 'RasponicsLog'
GDOCS_FEEDING_WORKSHEET_NAME = 'Feed Details'
GDOCS_TEMPS_WORKSHEET_NAME = 'Temperatures'

def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open(spreadsheet)
        return spreadsheet
    except Exception as ex:
        logging.error('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        logging.error('Google sheet login failed with error: %s' % ex)

def log_feeding_to_google(logtime,feed_type,feed_amount):

    sht = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    #
    # Try to open the worksheet, if it fails then create it
    #
    try:
        wks = sht.worksheet(GDOCS_FEEDING_WORKSHEET_NAME)
    except:
        logging.info('Worksheet %s does not exist, creating' % GDOCS_FEEDING_WORKSHEET_NAME)
        wks = sht.add_worksheet(title=GDOCS_FEEDING_WORKSHEET_NAME, rows="1", cols="3")

        wks.update_cell(1,1,"Date")
        wks.update_cell(1,2,"Type")
        wks.update_cell(1,3,"Amount (g)")

    #
    # Add a row with the data
    #
    try:
        wks.append_row((logtime, feed_type, feed_amount))
    except:
        logging.warning('Error appending a row to the feeding worksheet')

def log_temps_to_google(logtime,air_temp, humidity, tank_temp, sump_temp):

    sht = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    #
    # Try to open the worksheet, if it fails then create it
    #
    try:
        wks = sht.worksheet(GDOCS_TEMPS_WORKSHEET_NAME)
    except:
        logging.info('Worksheet %s does not exist, creating' % GDOCS_TEMPS_WORKSHEET_NAME)
        wks = sht.add_worksheet(title=GDOCS_TEMPS_WORKSHEET_NAME, rows="1", cols="5")

        wks.update_cell(1,1,"Date")
        wks.update_cell(1,2,"Air Temp")
        wks.update_cell(1,3,"Humidity")
        wks.update_cell(1,4,"Tank Temp")
        wks.update_cell(1,5,"Sump Temp")

    #
    # Add a row with the data
    #
    try:
        wks.append_row((logtime, air_temp, humidity, tank_temp, sump_temp))
    except:
        logging.warning('Error appending a row to the feeding worksheet')
