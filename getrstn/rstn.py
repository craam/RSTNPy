from __future__ import print_function

import datetime as dt
import os
import gzip

import numpy as np
import pandas as pd
import wget

from matplotlib.dates import DateFormatter

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from .exceptions import FileNotFoundOnServer, NoneFilename


class GetRSTN(object):

    """Download rstn 1 second data from noaa's site.

    :param day: Event's day.
    :type day: int or str
    :param month: Event's month.
    :type month: int or str
    :param year: Events' year.
    :type year: int or str
    :param station: Station (default: Sagamore Hill).
    :type station: str

    """

    def __init__(self, day, month, year, path, station='Sagamore Hill'):
        # pylint: disable-msg=R0913
        self._day = str(day)
        if len(self._day) == 1:
            self._day = '0' + self._day
        self._month = str(month)
        if len(self._month) == 1:
            self._month = '0' + self._month
        self._year = str(year)

        self._path = str(path)
        if self._path[-1] != "/":
            self._path += "/"
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        self._station = station
        self._filename = None
        self.rstn_data = None

    def get_filename(self):
        """Gets the filename.

        :returnss: Filename
        :rtype: str

        """

        return self._filename

    def __set_station_name(self):
        """Sets the station name as it is in noaa's site.

        :returns: The station name as it is in the site.
        :rtype: str

        """
        return self._station.lower().replace(' ', '-')

    def __change_month_upper(self):
        """Sets the month for the filename in upper case.

        :returns: The month in upper case.
        :rtype: str

        """
        months = [
            "JAN", "FEV", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
        ]

        # Returns the corresponding month to download the file.
        index = int(self._month) - 1
        return months[index]

    def __change_month_lower(self):
        """Sets the month for the filename in lowercase.

        :returns: The month in lower cas e.
        :rtype: str

        """

        months = [
            "jan", "fev", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"
        ]

        # Returns the corresponding month to download the file.
        index = int(self._month) - 1
        return months[index]

    def __set_file_extension_upper(self, file_gzip=True):
        """Creates the file extension upper case.

        :param file_gzip: Sets if the extension will have .gz.
        :type file_gzip: bool

        :returns: The file extension.
        :rtype: str
        """

        if self._station.lower() == "sagamore hill":
            extension = ".K7O"
        elif self._station.lower() == "san vito":
            extension = ".LIS"
        elif self._station.lower() == "palehua":
            extension = ".PHF"
        elif self._station.lower() == "learmonth":
            extension = ".APL"

        if file_gzip:
            return extension + ".gz"

        return extension

    def __set_file_extension_lower(self, file_gzip=True):
        """Creates the file extension lower case.

        :param file_gzip: Sets if the extension will have .gz.
        :type file_gzip: bool

        :returns: The file extension.
        :rtype: str
        """

        if self._station.lower() == "sagamore hill":
            extension = ".k7o"
        elif self._station.lower() == "san vito":
            extension = ".lis"
        elif self._station.lower() == "palehua":
            extension = ".phf"
        elif self._station.lower() == "learmonth":
            extension = ".apl"

        if file_gzip:
            return extension + ".gz"

        return extension

    def file_exists(self):
        """Checks if the file exists.

        :returns: True if the file exists.
        :rtype: bool

        """

        files = os.listdir(self._path)
        filename_upper = self.__set_filename(
            True) + self.__set_file_extension_lower(False)
        filename_lower = self.__set_filename(
            False) + self.__set_file_extension_lower(False)

        for _file in files:
            if _file in (filename_upper, filename_lower):
                self._filename = _file
                return True

        return False

    def __set_filename(self, upper):
        """Creates the file name.

        :param upper: Sets if the filename is going to be upper or lower case.
        :type upper: bool

        :returns: The filename.
        :rtype: str
        """

        if upper:
            filename = self._day + self.__change_month_upper() + self._year[2:]
        else:
            filename = self._day + self.__change_month_lower() + self._year[2:]

        return filename

    def __set_url(self, upper):
        """Creates the url of the file to be downloaded.

        Arguments:
            upper {bool} -- Used to try downloading both name in upper
                            and lower case.

        Returns:
            {str} -- The whole url.
        """

        station_name = self.__set_station_name()

        if upper:
            filename = self.__set_filename(True)
            file_extension = self.__set_file_extension_upper()
        else:
            filename = self.__set_filename(False)
            file_extension = self.__set_file_extension_lower()

        url = 'https://www.ngdc.noaa.gov/stp/space-weather/solar-data/'
        url += 'solar-features/solar-radio/rstn-1-second/'
        url += station_name + '/' + self._year + '/' + self._month + '/'
        url += filename + file_extension

        return url

    def download_data(self):
        """Downloads the file via https.

        :returns: True when the file was downloaded.
        :rtype: bool

        :raises FileNotFoundOnServer: If the file does not exist in noaa's
                                      website.

        """

        if self.file_exists():
            print("File already downloaded")
            return False

        # Tries to download with the file extension in upper case.
        # Then tries to download with the file extension in lower case.
        try:
            url = self.__set_url(True)
            filename = wget.download(url)
            os.rename(filename, self._path + filename)
        except HTTPError:
            try:
                url = self.__set_url(False)
                filename = wget.download(url)
                os.rename(filename, self._path + filename)
            except HTTPError:
                raise FileNotFoundOnServer("File not found on server.")

        self._filename = filename
        return True

    def decompress_file(self, download=False):
        """It doesn't really decompress the file, it saves the data
        inside in a different file with the same name.

        :param download: Downloads the file or not.
        :type download: bool

        :returns: File's final name.
        :rtype: str

        """

        if download:
            try:
                if not self.download_data():
                    return False
            except FileNotFoundOnServer:
                print("File does not exist on server")
                return False

        with gzip.open(self._path + self._filename, 'rb') as _file:
            file_content = _file.read()
            # Removes .gz from filename.
            final_name = self._filename.split('.gz')[0]
            with open(self._path + final_name, 'wb') as final_file:
                # Saves the content to a new file.
                final_file.write(file_content)

        os.remove(self._path + self._filename)
        self._filename = final_name
        return final_name

    def read_file(self):
        """Reads the file data and saves it in columns by frequency.

        :returns: The data in arrays.
        :rtype: dict

        :raises NoneFilename: If filename is not set.

        """
        if self._filename is None:
            raise NoneFilename

        rstn_data = {"time": [], "f245": [], "f410": [], "f610": [],
                     "f1415": [], "f2695": [], "f4995": [], "f8800": [],
                     "f15400": []
                     }

        with open(self._path + self._filename) as file:
            for line in file.readlines():
                line = line.split()

                if len(line) != 9:
                    continue

                year = int(line[0][4:8])
                month = int(line[0][8:10])
                day = int(line[0][10:12])
                hour = int(line[0][12:14])
                minute = int(line[0][14:16])
                second = int(line[0][16:18])

                date = dt.datetime(year, month, day, hour, minute, second)

                rstn_data["time"].append(date)
                rstn_data["f245"].append(line[1])
                rstn_data["f410"].append(line[2])
                rstn_data["f610"].append(line[3])
                rstn_data["f1415"].append(line[4])
                rstn_data["f2695"].append(line[5])
                rstn_data["f4995"].append(line[6])
                rstn_data["f8800"].append(line[7])
                rstn_data["f15400"].append(line[8])

        return rstn_data

    def create_dataframe(self):
        """Creates the dataframe with the file's data.

        :returns: The dataframe with the data.
        :rtype: pandas.DataFrame

        """

        try:
            data = self.read_file()
        except NoneFilename:
            raise Exception("File not found")

        columns = ["f245", "f410", "f610", "f1415",
                   "f2695", "f4995", "f8800", "f15400"]
        self.rstn_data = pd.DataFrame(data, columns=columns,
                                      index=data["time"])

        self.rstn_data = self.rstn_data.astype(np.int16)
        self.rstn_data.index = self.rstn_data.index.tz_localize("UTC")
        return self.rstn_data

    def plot(self):
        """Plots the file's data.

        :returns: Graphic's axes object for manipulation.
        :rtype: matplotlib.Axes

        """

        if self.rstn_data is None:
            if self.create_dataframe() is False:
                print("Can't plot data")
                return False

        ax = self.rstn_data.plot()
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

        return ax
