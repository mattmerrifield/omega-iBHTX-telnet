import telnetlib
import re
import datetime

__author__ = 'MMerrifield'

class iBHTX(object):
    def __init__(self, hostname, port):
        self.HOST = hostname
        self.PORT = port
        self.telnet = telnetlib.Telnet(hostname,port)
        self.column_headers = ['Ambient Temperature (C)', 'Ambient Pressure (mba)', 'Ambient Humidity (%RH)', 'Dew Point (F)']
        self.data_headers = ['T','P','H','D']
        self.units = ['C','mba','%','F']

        self.header_mapping = dict(zip(self.data_headers, self.column_headers))


    def parse_data(self, item):
        item = item.strip()
        header_regex = '|'.join(self.data_headers)
        units_regex = '|'.join(self.units)
        matching = r"(" + header_regex +r")([\d.]+)(" +units_regex + r")"
        match = re.search(matching, item)
        return match.groups()

    def get_line(self):
        data = {}
        timeout_counter = 0
        timeout_limit = 10
        while len(data) < len(self.column_headers) or timeout_counter > timeout_limit:
            item = self.telnet.read_until('\r')
            head, data_item, units = self.parse_data(item)
            column_heading = self.header_mapping[head]
            data[column_heading] = data_item
            timeout_counter += 1
        return data

    def listen(self):
         while True:
            line = self.get_line()
            time = datetime.datetime.now()
            print time, line
