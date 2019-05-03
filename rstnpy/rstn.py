import gzip
import os

from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List

from numpy import nan, int64
from pandas import DataFrame

from .exceptions import FilenameNotSetError, DataFrameNotCreatedError
from .rstndownloader import RSTNDownloader


class RSTNFile:
    def __init__(self, day: str, month: str, year: str, station: str) -> None:
        self.day = day
        self.month = month
        self.year = year
        self.station = station
        self.name = self.__set_default_name()
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

    def __change_month_upper(self) -> str:
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

    def __change_month_lower(self) -> str:
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

    def __set_file_extension_upper(self, file_gzip: bool = True) -> str:
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

        extension = "." + \
            self.__station_extensions[self.station.lower()]["upper"]

        if file_gzip:
            return extension + ".gz"

        return extension

    def __set_file_extension_lower(self, file_gzip: bool = True) -> str:
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

        extension = "." + \
            self.__station_extensions[self.station.lower()]["lower"]

        if file_gzip:
            return extension + ".gz"

        return extension

    def __set_filename(self, upper: bool) -> str:
        """Creates the filename.

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

    def __set_default_name(self) -> str:
        return self.__set_filename(True)

    def __format_station_for_url(self, station: str) -> str:
        """Formats the station name as it is in NOAA's site for the url.

        Returns
        -------
        str
            The station name as it is in the site url.

        """

        return station.lower().replace(' ', '-')


class RSTN:
    """Read RSTN files.

    Attributes
    ----------
    day: int
        Event's day.
    month: int
        Event's month.
    year: int
        Event's year.
    path: str
        Where the files are/will be stored.
    station: str
        Station.
    dataframe: pandas.DataFrame
        The dataframe containing the data. (default: None)

    """

    def __init__(self, day: int, month: int, year: int, path: str,
                 station: str) -> None:
        self.day = self.__format_day(day)
        self.month = self.__format_month(month)
        self.year = str(year)

        self.path = self.__validate_path(path)
        self.__station = station
        self.__filename = None

        self.downloader = RSTNDownloader(self.day, self.month, self.year,
                                         self.path, station)
        self.dataframe = None
        self.frequencies_columns = [
            "245", "410", "610", "1415",
            "2695", "4995", "8800", "15400"
        ]

    @property
    def filename(self) -> Union[str, None]:
        """Gets the filename.

        Returns
        -------
        str
            Filename

        """

        return self.__filename

    @property
    def station(self) -> str:
        """Gets the station name.

        Returns
        -------
        str
            Station name.

        """

        return self.__station

    def __format_day(self, day: int) -> str:
        """Formats the day as a string in the format dd.

        Parameters
        ----------
        day: int
            The day to be formatted.

        Returns
        -------
        day: str
            Formatted day.

        """

        formatted_day = str(day)
        if len(formatted_day) == 1:
            formatted_day = '0' + formatted_day

        return formatted_day

    def __format_month(self, month: int) -> str:
        """Formats the month as a string in the format mm.

        Parameters
        ----------
        month: int
            The month to be formatted.

        Returns
        -------
        month: str
            Formatted month.

        """

        formatted_month = str(month)
        if len(formatted_month) == 1:
            formatted_month = '0' + formatted_month

        return formatted_month

    def __validate_path(self, path: str) -> Path:
        """Validates the existence of a given path.

        Parameters
        ----------
        path: str
            The original path.

        Returns
        -------
        validated_path: Path
            The validated path.

        """
        validated_path = Path(path)

        if not validated_path.exists():
            validated_path.mkdir()

        return validated_path

    def __cast_to_int64(self, number) -> Union[int64, nan]:
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

    def decompress_file(self) -> str:
        """Gets gzipped file content.

        The method doesn't actually decompress the file. In reallity it reads
        the compressed data and writes it in a new file without
        the .gz extension.

        Returns
        -------
        str
            Final filename.

        """

        filename_gzip = str(self.__filename)
        path_to_gzip = self.path.joinpath(filename_gzip)

        with gzip.open(path_to_gzip, 'rb') as gzipped_file:
            file_content = gzipped_file.read()
            final_name = filename_gzip.split('.gz')[0]
            with Path(self.path.joinpath(final_name)).open("wb") as final_file:
                final_file.write(file_content)

        os.remove(Path(self.path.joinpath(filename_gzip)))

        self.__filename = final_name

        return final_name

    def __set_column_interval(self) -> int:
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

    def read_file(self) -> Dict[str, List[Union[int64, nan]]]:
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

        rstn_data = {"time": [], "245": [], "410": [], "610": [],
                     "f1415": [], "2695": [], "4995": [], "8800": [],
                     "15400": []
                     }

        interval = self.__set_column_interval()

        with Path(self.path.joinpath(self.__filename)).open("r") as fp:
            for line in fp.readlines():
                year = int(line[4:8])
                month = int(line[8:10])
                day = int(line[10:12])
                hour = int(line[12:14])
                minute = int(line[14:16])
                second = int(line[16:18])

                date = datetime(year, month, day, hour, minute, second)

                rstn_data["time"].append(date)
                rstn_data["245"].append(self.__cast_to_int64(
                    line[18:18+interval]))
                rstn_data["410"].append(self.__cast_to_int64(
                    line[18+interval:18+interval*2]))
                rstn_data["610"].append(self.__cast_to_int64(
                    line[18+interval*2:18+interval*3]))
                rstn_data["1415"].append(self.__cast_to_int64(
                    line[18+interval*3:18+interval*4]))
                rstn_data["2695"].append(self.__cast_to_int64(
                    line[18+interval*4:18+interval*5]))
                rstn_data["4995"].append(self.__cast_to_int64(
                    line[18+interval*5:18+interval*6]))
                rstn_data["8800"].append(self.__cast_to_int64(
                    line[18+interval*6:18+interval*7]))
                rstn_data["15400"].append(self.__cast_to_int64(
                    line[18+interval*7:]))

        return rstn_data

    def create_dataframe(self) -> DataFrame:
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
                "The file " + str(self.__filename) + " was not found.")

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
