from __future__ import print_function

import os
import gzip
import wget
from ftplib import FTP

class NoaaFTP:

    """Download solar data from noaa's FTP.

    Args:
        day (str or int):  event's day.
        month (str or int):  event's month.
        year (str or int):  events' year.
        station (str, optional):  Station (default Sagamore Hill).

    Attributes:
        day (str or int):  event's day.
        month (str or int):  event's month.
        year (str or int):  events' year.
        station (str, optional):  Station (default Sagamore Hill).
        filename (str): Name of the downloaded file.
        ABS_PATH (str): Absolute path fot the file.
    """

    def __init__(self, day, month, year, station='Sagamore Hill'):
        self.day = str(day)
        if len(self.day) == 1:
            self.day = '0' + self.day
        self.month = str(month)
        if len(self.month) == 1:
            self.month = '0' + self.month
        self.year = str(year)
        self.station = station
        self.ABS_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"


    def __set_station_name(self):
        return self.station.lower().replace(' ', '-')


    def __change_month_upper(self):
        months = [
            "JAN", "FEV", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OUT", "NOV", "DEC"
        ]

        # Returns the corresponding month to dowload the file.
        index = int(self.month) - 1
        return months[index]


    def __change_month_lower(self):
        months = [
            "jan", "fev", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "out", "nov", "dec"
        ]

        # Returns the corresponding month to dowload the file.
        index = int(self.month) - 1
        return months[index]


    def __set_file_extension_upper(self):

        if self.station.lower() == "sagamore hill":
            extension = ".K7O.gz"
        elif self.station.lower() == "san vito":
            extension = ".LIS.gz"
        elif self.station.lower() == "palehua":
            extension = ".PHF.gz"
        elif self.station.lower() == "learmonth":
            extension = ".APL.gz"

        return extension

    def __set_file_extension_lower(self):

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

        station_name = self.__set_station_name()

        filename = self.day + self.__change_month_upper() + self.year[2:]
        file_extension = self.__set_file_extension_upper()

        url = 'ftp://ftp.ngdc.noaa.gov/STP/space-weather/solar-data/'
        url += 'solar-features/solar-radio/rstn-1-second/'
        url += station_name + '/' + self.year + '/' + self.month + '/'

        # Tries to download with the file extension in lower case.
        # Then tries to download with the file extension in lower case.
        try:
            url += filename + file_extension
            filename = wget.download(url)
        except:
            url = url.split(filename)[0]
            filename = self.day + self.__change_month_lower() + self.year[2:]
            file_extension = self.__set_file_extension_lower()
            url += filename + file_extension
            wget.download(url)
        finally:
            self.filename = filename + file_extension


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

        os.rename(self.ABS_PATH + final_name[0],self.ABS_PATH + "data/" + final_name[0])
        os.remove(self.filename)


noaa = NoaaFTP(9, 4, 2002)
noaa.download_data()
noaa.decompress_file()
