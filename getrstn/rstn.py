"""
Edison Neto. This software downloads rstn data from noaa's site.

Copyright (C) 2018 Edison Neto
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from __future__ import print_function

import datetime as dt
import os
import gzip

import numpy as np
import pandas as pd
import wget

from matplotlib.dates import hours, num2date, DateFormatter

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from .exceptions import *


class GetRSTN(object):

    """Download solar data from noaa's site.

    Args:
        day {str or int} -- event's day.
        month {str or int} -- event's month.
        year {str or int} --  events' year.
        station {str, optional} -- Station (default Sagamore Hill).

    Attributes:
        day {str} -- event's day.
        month {str} -- event's month.
        year {str} -- events' year.
        station {str} --  Station (default Sagamore Hill).
        filename {str} -- Name of the downloaded file.
        path {str} -- Absolute path for the file.
        rstn_data {pandas.DataFrame} -- The data saved in a DataFrame.
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

        Returns:
            {str} -- Filename
        """

        return self._filename

    def __set_station_name(self):
        """Sets the station name as it is in noaa's site.

        Returns:
            {str} -- The station as in the site.
        """
        return self._station.lower().replace(' ', '-')

    def __change_month_upper(self):
        """Sets the month for the filename in upper case.

        Returns:
            {str} -- The month.
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

        Returns:
            {str} -- The month.
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

        Keyword Arguments:
            file_gzip {bool} -- Sets if the extension will have .gz.
                                (default: {True})

        Returns:
            {str} -- The extension.
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

        Keyword Arguments:
            file_gzip {bool} -- Sets if the extension will have .gz.
                                (default: {True})

        Returns:
            {str} -- The extension.
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
        """Sees if the file exists.

        Returns:
            {bool} -- True if the file exists.
        """

        arquivos = os.listdir(self._path)
        filename_upper = self.__set_filename(
            True) + self.__set_file_extension_lower(False)
        filename_lower = self.__set_filename(
            False) + self.__set_file_extension_lower(False)

        for arquivo in arquivos:
            if arquivo in (filename_upper, filename_lower):
                self._filename = arquivo
                return True

        return False

    def __set_filename(self, upper):
        """Creates the file name.

        Arguments:
            upper {bool} -- Sets if the file is going to be upper case
                            or lower case.

        Returns:
            {str} -- The file's name.
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

        Returns:
            {bool} -- True when the file was downloaded.

        Raises:
            FileNotFoundOnServer: The file does not exist.
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

        Keyword Arguments:
            download {bool} -- Downloads the file or not. (default: {False})

        Returns:
            {str} -- File's final name.
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

    def _read_file(self):
        """Reads the file.

        Returns:
            {numpy.ndarray} -- The data.

        Raises:
            NoneFilename: Filename is not set.
        """
        if self._filename is None:
            raise NoneFilename

        rstn_data = { "time": [], "f245": [], "f410": [], "f610": [],
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

        Returns:
            {pandas.DataFrame} -- The dataframe with the data.
        """

        try:
            data = self._read_file()
        except NoneFilename:
            print("No file")
            return False

        columns=["f245", "f410", "f610", "f1415",
                 "f2695", "f4995", "f8800", "f15400"]
        self.rstn_data = pd.DataFrame(data, columns=columns,
                                      index=data["time"])

        self.rstn_data = self.rstn_data.astype(np.int16)
        self.rstn_data.index = self.rstn_data.index.tz_localize("UTC")
        return self.rstn_data

    def plot(self):
        """Plots the file's data.

        Returns:
            {matplotlib.Axes} -- Graphic's axes for manipulation.
        """

        if self.rstn_data is None:
            if self.create_dataframe() is False:
                print("Can't plot data")
                return False

        ax = self.rstn_data.plot()
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

        return ax
