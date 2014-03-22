import telnetlib
import re
import datetime

__author__ = 'MMerrifield'

class iBTHX(object):
    HOST = '192.168.1.200'  # default ip address for iBTHX, per the manual
    PORT = 2000  # default telnet port for iBTHX, per the manual

    def __init__(self, hostname=None, port=None):
        self.HOST = self.HOST or hostname
        self.PORT = self.PORT or port

        self.telnet = telnetlib.Telnet(hostname, port)

        self.column_headers = ['Ambient Temperature (C)', 'Ambient Pressure (mba)', 'Ambient Humidity (%RH)', 'Dew Point (F)']
        self.packet_headers = ['T', 'P', 'H', 'D']
        self.unit_options = ['C', 'mba', '%', 'F']

        self.header_mapping = dict(zip(self.packet_headers, self.column_headers))


    def parse_data(self, item):
        """
        Returns a tuple (measurement_type, numeric_data, units)
        """
        # There's a lot of junk whitespace that comes from the read calls, usually. Strip it out.
        item = item.strip()

        # The first character is going to be one of the pre-defined header characters, as is the last units string
        # Construct a regex looking for (header)(data)(units) that separates them out.
        type_choices = '|'.join(self.packet_headers)
        unit_choices = '|'.join(self.unit_options)

        # parse out the data
        pattern = r"(" + type_choices + r")([\d.]+)(" + unit_choices + r")"
        parsed_item = re.search(pattern, item)
        type = parsed_item.group(1)
        data = parsed_item.group(2)
        units = parsed_item.group(3)

        # Return a tuple of (header)(data)(units)
        return (type, data, units)

    def get_line(self):
        """
        Returns a dictionary of all the data expected from the iBHTX. Gets one "set" of data
        """
        data = {}
        timeout_counter = 0
        timeout_limit = len(self.column_headers) + 2
        # Note: if we get too many repeat data items, something might be wrong.

        while len(data) < len(self.column_headers) or timeout_counter > timeout_limit:
            item = self.telnet.read_until('\r')
            head, data_item, units = self.parse_data(item)
            column_heading = self.header_mapping[head]
            data[column_heading] = data_item
            timeout_counter += 1
        return data

    def listen(self):
        """
        Constantly listens over the telnet port. Prints a stream of timestamped data.
        """
        while True:
            line = self.get_line()
            time = datetime.datetime.now()
            print time, line
