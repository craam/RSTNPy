from __future__ import print_function

import os
import gzip
import wget
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
        if int(self.year) < 2013:
            months = [
                "JAN", "FEV", "MAR", "APR", "MAY", "JUN",
                "JUL", "AUG", "SEP", "OUT", "NOV", "DEC"
            ]
        else:
            months = [
                "jan", "fev", "mar", "apr", "may", "jun",
                "jul", "aug", "sep", "out", "nov", "dec"
            ]

        # Returns the corresponding month to dowload the file.
        index = int(self.month) - 1
        return months[index]


    def set_file_extension(self):

        # After 2013 the extensions are in lower case.
        if int(self.year) < 2013:
            if self.station.lower() == "sagamore hill":
                extension = ".K7O.gz"
            elif self.station.lower() == "san vito":
                extension = ".LIS.gz"
            elif self.station.lower() == "palehua":
                extension = ".PHF.gz"
            elif self.station.lower() == "learmonth":
                extension = ".APL.gz"
        else:
            if self.station.lower() == "sagamore hill":
                extension = ".k7o.gz"
            elif self.station.lower() == "san vito":
                extension = ".lis.gz"
            elif self.station.lower() == "palehua":
                extension = ".phf.gz"
            elif self.station.lower() == "learmonth":
                extension = ".apl.gz"

        return extension


    def download_data(self):
        try:
            ftp = FTP('ftp.ngdc.noaa.gov')
            print(ftp.getwelcome())
            ftp.login()
        except:
            print("Connection not stablished.")
            return False

        station_name = self.set_station_name()

        filename = self.day + self.change_month() + self.year[2:]
        file_extension = self.set_file_extension()
        filename = filename + file_extension

        url = 'ftp://ftp.ngdc.noaa.gov/STP/space-weather/solar-data/'
        url += 'solar-features/solar-radio/rstn-1-second/'
        url += station_name + '/' + self.year + '/' + self.month + '/'
        url += filename

        filename = wget.download(url)

        self.filename = filename


    def decompress_file(self):
        """
        This function doesn't really decompress the file, it saves the data
        inside a different file with the same name.
        """

        # Checks if the filename varialabe exists.
        try:
            print(self.filename)
        except NameError:
            print("You need to download the file first.")
            return False

        with gzip.open(self.filename, 'rb') as _file:
            file_content = _file.read()
            # Removes .gz from filename.
            final_name = self.filename.split('.gz')
            with open(final_name[0], 'wb') as final_file:
                # Saves the content to a new file.
                final_file.write(file_content)

        os.remove(self.filename)


noaa = NoaaFTP(4, 9, 2002)
noaa.download_data()
noaa.decompress_file()
