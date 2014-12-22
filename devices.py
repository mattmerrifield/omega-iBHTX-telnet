import telnetlib
import logging
import re
import datetime
from collections import OrderedDict
__author__ = 'MMerrifield'

class Column(str):
    def __new__(cls, name, units):
        self = str.__new__(cls, name)
        self.units = units
        return self

    def __init__(self, name, units):
        super(Column, self).__init__(name)

class iBTHX(object):

    def __init__(self, hostname=None, port=None):
        self.host = hostname or '192.168.102.49'
        self.port = port or 2000

        self.telnet = telnetlib.Telnet(self.host, self.port)
        self.columns = OrderedDict([
            ("T", Column("Temperature", "C")),
            ("P", Column("Ambient Pressure", "mba")),
            ("H", Column("Humidity", "%")),
            ("D", Column("Dew Point", "F")),
        ])


    def parse_data(self, item):
        """
        Returns a tuple (measurement_type, numeric_data, units)
        """
        # There's a lot of junk whitespace that comes from the read calls, usually. Strip it out.
        item = item.strip()

        # The first character is going to be one of the pre-defined header characters, as is the last units string
        # Construct a regex looking for (header)(data)(units) that separates them out.
        type_choices = '|'.join([abbr for abbr in self.columns.keys()])
        unit_choices = '|'.join([col.units for col in self.columns.values()])

        # parse out the data
        pattern = r"({type})([\d.]+)({units})".format(type=type_choices, units=unit_choices)
        parsed_item = re.search(pattern, item)
        type = parsed_item.group(1)
        data = float(parsed_item.group(2))
        units = parsed_item.group(3)

        # Return a tuple of (header)(data)(units)
        return type, data, units

    def read_line(self):
        """
        Returns a dictionary of all the data expected from the iBHTX. Gets one "set" of data
        """
        data = {}
        timeout_counter = 0
        timeout_limit = len(self.columns) + 2
        # Note: if we get too many repeat data items, something might be wrong.

        while len(data) < len(self.columns) or timeout_counter > timeout_limit:
            item = self.telnet.read_until('\r')
            head, data_item, units = self.parse_data(item)
            data[head] = data_item
            timeout_counter += 1
        returndata = OrderedDict([(column, data[abbr]) for abbr, column in self.columns.iteritems()])
        return returndata


if __name__ == '__main__':
    ibthx = iBTHX()
    log = logging.getLogger(__name__)
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    while True:
        line = ibthx.read_line()
        time = datetime.datetime.now().isoformat()
        msg = "{{{}: {}}}".format(str(time), line)
        log.info(msg)