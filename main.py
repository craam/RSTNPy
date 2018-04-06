from __future__ import print_function

import os
import gzip
from ftplib import FTP

class NoaaFTP:

    def __init__(self, day, month, year, station='Sagamore Hill'):
        self.day = str(day)
        if len(self.day) == 1:
            self.day = '0' + self.day
        self.month = str(month)
        if len(self.month) == 1:
            self.month = '0' + self.month
        self.year = str(year)
        self.station = station


    def set_station_name(self):
        return self.station.lower().replace(' ', '-')


    def change_month(self):
        months = [
            "JAN", "FEV", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OUT", "NOV", "DEC"
        ]

        # Returns the corresponding month to dowload the file.
        index = int(self.month) - 1
        return months[index]


    def set_file_extension(self):
        if self.station.lower() == "sagamore hill":
            extension = ".K7O.gz"
        elif self.station.lower() == "san vito":
            extension = ".lis.gz"
        elif self.station.lower() == "palehua":
            extension = ".phf.gz"
        elif self.station.lower() == "learmonth":
            extension = ".apl.gz"

        return extension


    def download_data(self):
        ftp = FTP('ftp.ngdc.noaa.gov')
        ftp.login()

        station_name = self.set_station_name()
        ftp.cwd('STP/space-weather/solar-data/solar-features/solar-radio/rstn-1-second')

        # Sets the path for the file.
        ftp.cwd(station_name + '/' + self.year + '/' + self.month)

        filename = self.day + self.change_month() + self.year[2:]
        file_extension = self.set_file_extension()
        filename = filename + file_extension
        download_name = 'RETR ' + filename + file_extension

        # Absolute path for the file
        local_file = os.path.dirname(os.path.abspath(__file__)) + '/' + filename
        #ftp.retrbinary(download_name, open(local_file, 'wb').write)

        ftp.quit()

        print("File downloaded.")
        self.filename = filename


    def decompress_file(self):
        """
        This function doesn't really decompress the file, it saves the data
        inside a different file with the same name.
        """
        with gzip.open(self.filename, 'rb') as _file:
            file_content = _file.read()
            # Removes .gz from filename.
            final_name = self.filename.split('.gz')
            with open(final_name[0], 'wb') as final_file:
                # Saves the content to a new file.
                final_file.write(file_content)
