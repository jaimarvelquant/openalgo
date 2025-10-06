import pytz
import threading
import datetime as dt

logger_lock = threading.Lock()


class Logger:
    def __init__(self, db):
        self.db = db

    def log(self, message, level, port_id=None):
        global logger_lock
        with logger_lock:
            now = dt.datetime.now(tz=pytz.timezone("Asia/Kolkata")).replace(microsecond=0)

            log_txt = f"{now.strftime('%c')}\t(#{port_id})\t[{level.upper()}]\t{message}"
            with open("../webapp/log.txt", "a") as log_file:
                log_file.write(log_txt + "\n")

            print(log_txt) # For showing log in out.log in server, don't remove it
            self.db.add_log(now, message, level, port_id)