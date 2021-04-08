from datetime import datetime
import time
from log import loginfo
from log.loginfo import LogFile

 
log = LogFile(__name__).getlog()
def WekSear():
    apply_time = time.time()
    apply_time = datetime.utcfromtimestamp(apply_time)
    time_str = apply_time.strftime("%Y-%m-%d %H:%M:%S")
    apply_hour = time_str.split(" ")[1].split(":")[0]
    apply_week = datetime.strptime(time_str.split(" ")[0], "%Y-%m-%d").weekday()
    return apply_week