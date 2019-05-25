import gzip

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from numpy import int64, nan
from pandas import DataFrame

from .exceptions import FilenameNotSetError, DataFrameNotCreatedError
from .rstndownloader import RSTNDownloader
from .rstnfile import RSTNFile


class RSTN:
    """Read RSTN files.

    Attributes
    ----------
    year: int
        Event's year.
    month: int
        Event's month.
    day: int
        Event's day.
    path: Path
        Where the files are/will be stored.
    station: str
        Station.
    dataframe: pandas.DataFrame
        The dataframe containing the data. (default: None)

    """

    def __init__(self, year: int, month: int, day: int, path: str,
                 station: str) -> None:
        self.year = str(year)
        self.month = self.__format_month(month)
        self.day = self.__format_day(day)

        self.path = self.__validate_path(path)
        self.__station = station
        self.__file: RSTNFile = RSTNFile(self.year, self.month, self.day,
                                         self.station)

        self.downloader = RSTNDownloader(self.year, self.month, self.day,
                                         self.path, station)
        self.dataframe = None
        self.frequencies_columns = [
            "245", "410", "610", "1415",
            "2695", "4995", "8800", "15400"
        ]

    @property
    def filename(self) -> str:
        """Gets the filename.

        Returns
        -------
        str
            Filename

        """

        return self.__file.name

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

    @staticmethod
    def is_gzippep(filename: Path) -> bool:
        try:
            gzip.open(filename, 'rb').read()
            return True
        except OSError:
            return False

    def decompress_file(self, filename: str) -> str:
        """Gets gzipped file content.

        The method doesn't actually decompress the file. In reallity it reads
        the compressed data and writes it in a new file without
        the .gz extension.

        Returns
        -------
        str
            Final filename.

        """

        path_to_gzip = self.path.joinpath(filename)

        if not self.is_gzippep(path_to_gzip):
            self.__file.name = filename
            return filename

        with gzip.open(path_to_gzip, 'rb') as gzipped_file:
            file_content = gzipped_file.read()
            final_name = filename.split('.gz')[0]
            with self.path.joinpath(final_name).open("wb") as final_file:
                final_file.write(file_content)

        self.path.joinpath(filename).unlink()

        self.__file.name = final_name

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

    def read_file(self) -> Dict[str, List]:
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

        if self.__file is None:
            raise FilenameNotSetError(
                "The file " + self.__file.name + " has an invalid name.")

        rstn_data: Dict[str, List] = {
            "time": [], "245": [], "410": [], "610": [],
            "1415": [], "2695": [], "4995": [], "8800": [],
            "15400": []
        }

        interval = self.__set_column_interval()

        with self.path.joinpath(self.__file.name).open("r") as fp:
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
                "The file " + self.__file.name + " was not found.")

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
