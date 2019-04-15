from __future__ import print_function

import gzip
import os

from datetime import datetime

from numpy import nan, int64
from pandas import DataFrame

from .rstndownloader import RSTNDownloader

from .exceptions import FilenameNotSetError, DataFrameNotCreatedError


class RSTN(object):
    """Read RSTN files.

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
        Station.
    dataframe: pandas.DataFrame
        The dataframe containing the data. (default: None)

    """

    def __init__(self, day, month, year, path, station):
        self.day = self.__format_day(day)
        self.month = self.__format_month(month)
        self.year = str(year)

        self.path = self.__validade_path(path)
        self.__station = station
        self.__filename = None

        self.downloader = RSTNDownloader(day, month, year, path, station)
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

    @property
    def filename(self):
        """Gets the filename.

        Returns
        -------
        str
            Filename

        """

        return self.__filename

    @property
    def station(self):
        """Gets the station name.

        Returns
        -------
        str
            Station name.

        """

        return self.__station

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

    def __validade_path(self, path):
        if path[-1] != "/":
            path += "/"

        if not os.path.exists(path):
            os.mkdir(path)

        return path

    def __cast_to_int64(self, number):
        """Casts a number to the numpy int64 type.

        Parameters
        ----------
        number: int or str
            The number that will be changed.

        Returns
        -------
        number: numpy.int64 or numpy.nan
            The number as a int64 or NaN.

        """

        try:
            number = int64(number)
        except ValueError:
            number = nan

        return number

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
                self.__filename = _file
                return True

        return False

    def decompress_file(self):
        """Gets gzipped file content.

        The method doesn't actually decompress the file. In reallity it reads
        the compressed data and writes it in a new file without
        the .gz extension.

        Returns
        -------
        str
            File's final name.

        """

        path_to_gzip = os.path.join(self.path, self.__filename)
        with gzip.open(path_to_gzip, 'rb') as gzipped_file:
            file_content = gzipped_file.read()
            # Separates the .gz extension from the filename.
            final_name = self.__filename.split('.gz')[0]
            with open(os.path.join(self.path, final_name), 'wb') as final_file:
                # Saves the content to a new file.
                final_file.write(file_content)

        os.remove(os.path.join(self.path, self.__filename))
        self.__filename = final_name

        return final_name

    def __set_column_interval(self):
        """Sets the interval for each frequency column.

        The column size changes from time to time.

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

        if self.__filename is None:
            raise FilenameNotSetError(
                "The file " + str(self.__filename) + " has an invalid name.")

        rstn_data = {"time": [], "f245": [], "f410": [], "f610": [],
                     "f1415": [], "f2695": [], "f4995": [], "f8800": [],
                     "f15400": []
                     }

        interval = self.__set_column_interval()

        with open(os.path.join(self.path, self.__filename)) as _file:
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
                "The file " + self.__filename + " was not found.")

        self.dataframe = DataFrame(data, columns=self.frequencies_columns,
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
