from __future__ import print_function

import os
import gzip

import numpy as np
import pandas as pd
import wget

from datetime import datetime

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from .exceptions import (
    FileNotFoundOnServer, FilenameNotSetError,
    DataFrameNotCreatedError
)


class GetRSTN(object):
    """Download rstn 1 second data from noaa's site.

    Base url to ngdc data is: https://www.ngdc.noaa.gov/

    Rstn 1 second data is under Solar-Terrestrial Physics(STP):
    stp/space-weather/solar-data/solar-features/solar-radio/rstn-1-second/

    Attributes
    ----------
    day: int or str
        Event's day.
    month: int or str
        Event's month.
    year: int or str
        Event's year.
    path: str
        Where the files are/will be stored.
    station: str
        Station (default: Sagamore Hill).
    dataframe: pandas.DataFrame
        The dataframe containing the data. (default: None)

    """

    def __init__(self, day, month, year, path, station='Sagamore Hill'):
        self.day = self.__format_day(day)
        self.month = self.__format_month(month)
        self.year = str(year)

        self.path = str(path)
        if self.path[-1] != "/":
            self.path += "/"
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self._station = station
        self._filename = None
        self.dataframe = None
        self.__station_extensions = {
            "sagamore hill": {
                "lower": "k7o", "upper": "K7O"
            },
            "san vito": {
                "lower": "lis", "upper": "LIS"
            },
            "palehua": {
                "lower": "phf", "upper": "PHF"
            },
            "learmonth": {
                "lower": "apl", "upper": "APL"
            }
        }
        self.frequencies_columns = [
                "f245", "f410", "f610", "f1415",
                "f2695", "f4995", "f8800", "f15400"
        ]

    def __format_day(self, day):
        """Formats the day as a string in the format dd.

        Parameters
        ----------
        day: str or int
            The day to be formatted.

        Returns
        -------
        day: str
            Formatted day.

        """

        day = str(day)
        if len(day) == 1:
            day = '0' + day

        return day

    def __format_month(self, month):
        """Formats the month as a string in the format mm.

        Parameters
        ----------
        month: str or int
            The month to be formatted.

        Returns
        -------
        month: str
            Formatted month.

        """

        month = str(month)
        if len(month) == 1:
            month = '0' + month

        return month

    @property
    def get_filename(self):
        """Gets the filename.

        Returns
        -------
        str
            Filename

        """

        return self._filename

    def __format_station_for_url(self, station):
        """Formats the station name as it is in NOAA's site for the url.

        Returns
        -------
        str
            The station name as it is in the site url.

        """

        return station.lower().replace(' ', '-')

    def __cast_to_int64(self, number):
        """Casts a number to the numpy int64 type.

        Parameters
        ----------
        number: int or str
            The number that will be changed.

        Returns
        -------
        number: np.int64 or np.nan
            The number as a int64 or NaN.

        """

        try:
            number = np.int64(number)
        except ValueError:
            number = np.nan

        return number

    def __change_month_upper(self):
        """Sets the month for the filename in upper case.

        Returns
        -------
        str
            The month in upper case.

        """

        months = [
            "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
        ]

        # Returns the corresponding month to download the file.
        index = int(self.month) - 1
        return months[index]

    def __change_month_lower(self):
        """Sets the month for the filename in lowercase.

        Returns
        -------
        str
            The month in lower case.

        """

        months = [
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"
        ]

        # Returns the corresponding month to download the file.
        index = int(self.month) - 1
        return months[index]

    def __set_file_extension_upper(self, file_gzip=True):
        """Creates the file extension upper case.

        Parameters
        ----------
        file_gzip: bool
            Sets if the extension will have .gz.

        Returns
        -------
        str
            The file extension.

        """

        extension = "." + self.__station_extensions[self._station.lower()]["upper"]

        if file_gzip:
            return extension + ".gz"

        return extension

    def __set_file_extension_lower(self, file_gzip=True):
        """Creates the file extension lower case.


        Parameters
        ----------
        file_gzip: bool
            Sets if the extension will have .gz.

        Returns
        -------
        str
            The file extension.

        """

        extension = "." + self.__station_extensions[self._station.lower()]["lower"]

        if file_gzip:
            return extension + ".gz"

        return extension

    def file_exists(self):
        """Checks if the file exists.

        Returns
        -------
        bool
            If the file exists.

        """

        files = os.listdir(self.path)
        filename_upper = self.__set_filename(
            True) + self.__set_file_extension_upper(False)
        filename_lower = self.__set_filename(
            False) + self.__set_file_extension_lower(False)

        for _file in files:
            if _file in (filename_upper, filename_lower):
                self._filename = _file
                return True

        return False

    def __set_filename(self, upper):
        """Creates the file name.

        Parameters
        ----------
        upper: bool
            Sets if the filename is going to be upper or lower case.

        Returns
        -------
        str
            The filename.

        """

        if upper:
            filename = self.day + self.__change_month_upper() + self.year[2:]
        else:
            filename = self.day + self.__change_month_lower() + self.year[2:]

        return filename

    def __set_url(self, upper):
        """Creates the url of the file to be downloaded.

        Parameters
        ----------
        upper: bool
            Used to try downloading both name in upper and lower case.

        Returns
        -------
        str
            The whole url.

        """

        station_name = self.__format_station_for_url(self._station)

        if upper:
            filename = self.__set_filename(True)
            file_extension = self.__set_file_extension_upper()
        else:
            filename = self.__set_filename(False)
            file_extension = self.__set_file_extension_lower()

        url = "https://www.ngdc.noaa.gov/stp/space-weather/solar-data/"
        url += "solar-features/solar-radio/rstn-1-second/"
        url += station_name + '/' + self.year + '/' + self.month + '/'
        url += filename + file_extension

        return url

    def download_file(self):
        """Downloads the file via https.

        Returns
        -------
        bool
            True when the file was downloaded.

        Raises
        ------
        FileNotFoundOnServer
            If the file does not exist in noaa's website.

        """

        # Tries to download with the file extension in upper case.
        # Then tries to download with the file extension in lower case.
        try:
            url = self.__set_url(upper=True)
            filename = wget.download(url)
            os.rename(filename, os.path.join(self.path, filename))
        except HTTPError:
            url = self.__set_url(upper=False)
            try:
                filename = wget.download(url)
                os.rename(filename, os.path.join(self.path, filename))
            except HTTPError:
                raise FileNotFoundOnServer(
                    "The file on: " + url + " was not found on server.")

        self._filename = filename
        return True

    def decompress_file(self):
        """Gets gzipped file content.

        It doesn't decompress the file. It reads the compressed data and
        writes it in a new file without the .gz extension.

        Returns
        -------
        str
            File's final name.

        """

        with gzip.open(os.path.join(self.path, self._filename), 'rb') as gzipped_file:
            file_content = gzipped_file.read()
            # Separates the .gz extension from the filename.
            final_name = self._filename.split('.gz')[0]
            with open(os.path.join(self.path, final_name), 'wb') as final_file:
                # Saves the content to a new file.
                final_file.write(file_content)

        os.remove(os.path.join(self.path, self._filename))
        self._filename = final_name

        return final_name

    def read_file(self):
        """Reads the file data and saves it in columns by frequency.

        The first column is 18 digits long, the first 4 indicating the station,
        the others the timestamp. Each column for the frequency is 6 digits
        long if the year before 2007, if the year is 2008 or later than the
        column is 7 digits long.

        Returns
        -------
        dict
            The data in arrays.

        Raises
        ------
        FilenameNotSetError
            If filename is not set.

        """

        if self._filename is None:
            raise FilenameNotSetError(
                "The file " + str(self._filename) + " has an invalid name.")

        rstn_data = {"time": [], "f245": [], "f410": [], "f610": [],
                     "f1415": [], "f2695": [], "f4995": [], "f8800": [],
                     "f15400": []
                     }

        interval = self.__set_column_interval()

        with open(os.path.join(self.path, self._filename)) as _file:
            for line in _file.readlines():
                year = int(line[4:8])
                month = int(line[8:10])
                day = int(line[10:12])
                hour = int(line[12:14])
                minute = int(line[14:16])
                second = int(line[16:18])

                date = datetime(year, month, day, hour, minute, second)

                rstn_data["time"].append(date)
                rstn_data["f245"].append(self.__cast_to_int64(
                    line[18:18+interval]))
                rstn_data["f410"].append(self.__cast_to_int64(
                    line[18+interval:18+interval*2]))
                rstn_data["f610"].append(self.__cast_to_int64(
                    line[18+interval*2:18+interval*3]))
                rstn_data["f1415"].append(self.__cast_to_int64(
                    line[18+interval*3:18+interval*4]))
                rstn_data["f2695"].append(self.__cast_to_int64(
                    line[18+interval*4:18+interval*5]))
                rstn_data["f4995"].append(self.__cast_to_int64(
                    line[18+interval*5:18+interval*6]))
                rstn_data["f8800"].append(self.__cast_to_int64(
                    line[18+interval*6:18+interval*7]))
                rstn_data["f15400"].append(self.__cast_to_int64(
                    line[18+interval*7:]))

        return rstn_data

    def __set_column_interval(self):
        """Sets the interval for each frequency column.

        Returns
        -------
        interval: int
            The column interval size.

        """

        if int(self.year) >= 2015:
            return 8
        elif int(self.year) >= 2008:
            return 7
        else:
            return 6

    def create_dataframe(self):
        """Creates the dataframe with the file's data.

        Returns
        -------
        pandas.DataFrame
            The dataframe with the data.

        Raises
        ------
        FileNotFoundError
            If the filename is not set, therefore, it can't be found.

        """

        try:
            data = self.read_file()
        except FilenameNotSetError:
            raise FileNotFoundError(
                "The file " + self._filename + " was not found.")

        self.dataframe = pd.DataFrame(data, columns=self.frequencies_columns,
                                      index=data["time"])

        self.dataframe.index = self.dataframe.index.tz_localize("UTC")

        return self.dataframe

    def plot(self):
        """Plots the file's data.

        Returns
        -------
        axis: matplotlib.Axes
            Graphic's axes object for manipulation.

        Raises
        ------
        DataFrameNotCreatedError:
            If the dataframe was not created before this method is called.

        """

        if self.dataframe is None:
            raise DataFrameNotCreatedError(
                "Can't plot data. Dataframe was not created.")

        axis = self.dataframe.plot()

        return axis
