import sched
import time
import subprocess
event_schedule = sched.scheduler(time.time, time.sleep)

def ping_sites():
    subprocess.call(["python", "ping_site.py"])
    event_schedule.enter(1, 1, ping_sites)


event_schedule.enter(1, 1, ping_sites)
event_schedule.run()
