from datetime import datetime


class RSTNFile:
    """RSTN filename manipulation tools.

    Attributes
    ----------
    day: str
        Event's day.
    month: str
        Event's month.
    year: str
        Event's year.
    station: str
        Station.
    name: str
        Filename
    __station_extensions: Dict
        All possible file extensions for each station.

    """

    def __init__(self, year: str, month: str, day: str, station: str) -> None:
        self.year = year
        self.month = month
        self.day = day
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

    def set_file_extension_upper(self, file_gzip: bool = True) -> str:
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

    def set_file_extension_lower(self, file_gzip: bool = True) -> str:
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

    def set_filename(self, upper: bool) -> str:
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
        """Sets the default filename.

        Returns
        -------
        str
            The filename

        """
        return self.set_filename(True)

    def format_station_for_url(self) -> str:
        """Formats the station name as it is in NOAA's site for the url.

        Returns
        -------
        str
            The station name as it is in the site url.

        """

        formatted_station = self.station.lower().replace(' ', '-')

        return formatted_station

    def is_date_valid(self):
        """Checks if the date is valid.

        Returns
        -------
        bool
            If the date is valid.

        """

        try:
            year = int(self.year)
            month = int(self.month)
            day = int(self.day)
            datetime(year, month, day)
            return True
        except ValueError:
            return False
