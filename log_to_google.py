import gspread
from oauth2client.service_account import ServiceAccountCredentials

GDOCS_OAUTH_JSON = '/home/hburke/rasponics/5b689121080b.json'
GDOCS_SPREADSHEET_NAME = 'FeedLog'
GDOCS_WORKSHEET_NAME = 'Feed Details'

def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open(spreadsheet)
        return spreadsheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)

def log_to_google(logtime,feed_type,feed_amount):

    sht = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

#    for worksheet in sht.worksheets():
#        print worksheet.title

    #
    # Try to open the worksheet, if it fails then create it
    #
    try:
        wks = sht.worksheet(GDOCS_WORKSHEET_NAME)
    except:
        print "Sheet does not exist, creating"
        wks = sht.add_worksheet(title=GDOCS_WORKSHEET_NAME, rows="1", cols="3")

        wks.update_cell(1,1,"Date")
        wks.update_cell(1,2,"Type")
        wks.update_cell(1,3,"Amount (g)")

    #
    # Add a row with the data
    #
    try:
        wks.append_row((logtime, feed_type, feed_amount))
    except:
        print('Append error')

