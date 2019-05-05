from pathlib import Path
from urllib.error import HTTPError

from requests import get

from .exceptions import FileNotFoundOnServerError
from .rstnfile import RSTNFile


class RSTNDownloader:
    """Download rstn 1 second data from NOAA's site.

    Base url to NGDC data is: https://www.ngdc.noaa.gov/

    Rstn 1 second data is under Solar-Terrestrial Physics(STP):
    stp/space-weather/solar-data/solar-features/solar-radio/rstn-1-second/

    Attributes
    ----------
    year: int or str
        Event's year.
    month: int or str
        Event's month.
    day: int or str
        Event's day.
    path: str
        Where the files are/will be stored.
    __station: str
        Station.
    __file: RSTNFile
        The RSTNFile object.
    __base_uri: str
        The base uri to noaa's.

    """

    def __init__(self, year: str, month: str, day: str, path: Path,
                 station: str) -> None:
        self.year = year
        self.month = month
        self.day = day
        self.path = path
        self.__file = RSTNFile(year, month, day, station)
        self.__station = station
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

    def file_exists(self) -> bool:
        """Checks if the file exists.

        Returns
        -------
        bool
            If the file exists.

        """

        filename_upper = self.__file.set_filename(
            True) + self.__file.set_file_extension_upper(False)
        filename_lower = self.__file.set_filename(
            False) + self.__file.set_file_extension_lower(False)

        if Path(self.path.joinpath(filename_upper)).exists():
            return True

        if Path(self.path.joinpath(filename_lower)).exists():
            return True

        return False

    def __set_url(self, upper: bool) -> str:
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

        station_name = self.__file.format_station_for_url(self.__station)

        if upper:
            filename = self.__file.set_filename(True)
            file_extension = self.__file.set_file_extension_upper()
        else:
            filename = self.__file.set_filename(False)
            file_extension = self.__file.set_file_extension_lower()

        url = self.__base_uri + "/stp/space-weather/solar-data/"
        url += "solar-features/solar-radio/rstn-1-second/"
        url += station_name + '/' + self.year + '/' + self.month + '/'
        url += filename + file_extension

        return url

    def __download(self, upper: bool) -> str:
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
        filename = self.__file.set_filename(upper)

        if upper:
            filename += self.__file.set_file_extension_upper()
        else:
            filename += self.__file.set_file_extension_lower()

        r = get(url, allow_redirects=False)
        if r.status_code != 200:
            raise HTTPError(url, r.status_code, "HTTP error", r.headers, "")

        with open(filename, 'wb') as fp:
            fp.write(r.content)

        return filename

    def download_file(self) -> str:
        """Downloads the file via https.

        Tries to download with the file extension in upper case.
        Then tries to download with the file extension in lower case.

        Returns
        -------
        filename: str
            The downloaded gzipped filename.

        Raises
        ------
        FileNotFoundOnServer
            If the file does not exist in noaa's website.

        """

        try:
            filename = self.__download(upper=True)
        except HTTPError:
            try:
                filename = self.__download(upper=False)
            except HTTPError:
                url = self.__set_url(upper=False)
                raise FileNotFoundOnServerError(
                    "The file on: " + url + " was not found on server.")

        Path(filename).rename(self.path.joinpath(filename))
        return filename
