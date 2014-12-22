from devices import iBTHX
import logging
from datetime import datetime
from logging import handlers

__author__ = 'MMerrifield'

class TimedRotatingFileHanderWithHeader(handlers.TimedRotatingFileHandler):
    def __init__(self, logger=None, header=None, *args, **kwargs):
        super(TimedRotatingFileHanderWithHeader, self).__init__(*args, **kwargs)
        self.header = header
        self.logger = logger

    def doRollover(self):
        super(TimedRotatingFileHanderWithHeader, self).doRollover()
        if self.header is not None:

            # Kind of a horrible hack, actually.
            # Makes sure there's a header on top of every log file.
            self.logger.info(self.header)



device = iBTHX()
header = " | ".join(["{}".format(col, col.units) for col in device.columns.values()])

# Logging Setup
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
format = logging.Formatter('[%(asctime)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
# Log file
rotating_logfile = TimedRotatingFileHanderWithHeader(logger=log, header=header, filename="iBTHX-humidity.log", when="D")
rotating_logfile.setFormatter(format)
rotating_logfile.setLevel(logging.DEBUG)
log.addHandler(rotating_logfile)
# Console
console = logging.StreamHandler()
console.setFormatter(format)
console.setLevel(logging.DEBUG)
log.addHandler(console)

# Main program
log.info(header)
while True:
    data = device.read_line()
    msg = " | ".join(["{} {}".format(v, k.units).rjust(len(k)) for k, v in data.iteritems()])
    log.info(msg)



