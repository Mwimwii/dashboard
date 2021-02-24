import datetime

def now():
    return datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    
def timestamp_now():
    now = datetime.now()
    # timestamp = datetime.timestamp(now)
    timestamp = datetime.datetime.utcnow()
    return timestamp

class Logger(object):
    def __init__(self):
        self.log = []

    def logger(self, msg, data, stdout=True, stderr=False):
        if stderr:
            msg = f'{now()}: [ERROR] {str(msg)}'
        else:
            msg = f'{now()}: {str(msg)}'

        if stdout:
            print(msg)
        self.log.append(data)

    def get_logs(self, clear=False):
        data_log = self.log
        if clear:
            self.log = []
        return data_log
        