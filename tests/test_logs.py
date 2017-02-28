import time
import sys
sys.path.insert(0,'..')
import log_to_rest_db as RLOG
import log_to_google as GLOG

feed = 13.1415768

RLOG.update_feeding_log('AM4000', feed)
GLOG.update_feeding_log('AM4000', feed)

airtemp=90.9
humidity=43.7
tanktoptemp=74.4
tankbtmtemp=74.8
GB_duration=757
GB_direction='v'
GB_last_transition=time.time()
pump_status=1
airpump_status=1

RLOG.update_status_log(airtemp,humidity,tanktoptemp,tankbtmtemp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status)
GLOG.update_status_log(airtemp,humidity,tanktoptemp,tankbtmtemp,GB_duration,GB_direction,GB_last_transition,pump_status,airpump_status)
