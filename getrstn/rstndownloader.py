import os.path

from pathlib import Path

from requests import get

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from .exceptions import FileNotFoundOnServer


class RSTNDownloader(object):
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
    __station: str
        Station.
    __filename: str
        The filename.
    __base_uri: str
        The base uri to noaa's.

    """

    def __init__(self, day, month, year, path, station):
        self.day = day
        self.month = month
        self.year = str(year)
        self.path = path
        self.__station = station
        self.__filename = None
        self.__base_uri = "https://www.ngdc.noaa.gov"
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

        extension = "." + \
            self.__station_extensions[self.__station.lower()]["upper"]

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

        extension = "." + \
            self.__station_extensions[self.__station.lower()]["lower"]

        if file_gzip:
            return extension + ".gz"

        return extension

    def __set_filename(self, upper):
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

    def file_exists(self):
        """Checks if the file exists.

        Returns
        -------
        bool
            If the file exists.

        """

        filename_upper = self.__set_filename(
            True) + self.__set_file_extension_upper(False)
        filename_lower = self.__set_filename(
            False) + self.__set_file_extension_lower(False)

        if Path(self.path.joinpath(filename_upper)).exists():
            return True

        if Path(self.path.joinpath(filename_lower)).exists():
            return True

        return False

    def __format_station_for_url(self, station):
        """Formats the station name as it is in NOAA's site for the url.

        Returns
        -------
        str
            The station name as it is in the site url.

        """

        return station.lower().replace(' ', '-')

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

        station_name = self.__format_station_for_url(self.__station)

        if upper:
            filename = self.__set_filename(True)
            file_extension = self.__set_file_extension_upper()
        else:
            filename = self.__set_filename(False)
            file_extension = self.__set_file_extension_lower()

        url = self.__base_uri + "/stp/space-weather/solar-data/"
        url += "solar-features/solar-radio/rstn-1-second/"
        url += station_name + '/' + self.year + '/' + self.month + '/'
        url += filename + file_extension

        return url

    def __download(self, upper):
        """Downloads the gzipped file.

        Returns
        -------
        filename: str
            the saved filename.

        Raises
        ------
        HttpError
            Raised if the status code of the response is not 200.

        """

        url = self.__set_url(upper)
        filename = self.__set_filename(upper)

        if upper:
            filename += self.__set_file_extension_upper()
        else:
            filename += self.__set_file_extension_lower()

        r = get(url, allow_redirects=False)
        if r.status_code != 200:
            raise HTTPError(url, r.status_code, "HTTP error", r.headers, "")

        open(filename, 'wb').write(r.content)
        return filename

    def download_file(self):
        """Downloads the file via https.

        Returns
        -------
        filename: str
            The downloaded gzipped filename.

        Raises
        ------
        FileNotFoundOnServer
            If the file does not exist in noaa's website.

        """

        # Tries to download with the file extension in upper case.
        # Then tries to download with the file extension in lower case.
        try:
            filename = self.__download(upper=True)
            os.rename(filename, Path(self.path.joinpath(filename)))
        except HTTPError:
            try:
                filename = self.__download(upper=False)
                os.rename(filename, Path(self.path.joinpath(filename)))
            except HTTPError:
                url = self.__set_url(upper=False)
                raise FileNotFoundOnServer(
                    "The file on: " + url + " was not found on server.")

        return filename
