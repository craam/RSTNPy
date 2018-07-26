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

import os
import gzip
import wget

from ftplib import FTP

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError


class GetRSTN:

    """Download solar data from noaa's FTP.

    Args:
        day {str or int} -- event's day.
        month {str or int} -- event's month.
        year {str or int} --  events' year.
        station {str, optional} -- Station (default Sagamore Hill).

    Attributes:
        day {str} -- event's day.
        month {str} -- event's month.
        year {str} -- events' year.
        station {str, optional} --  Station (default Sagamore Hill).
        filename {str} -- Name of the downloaded file.
        path {str} -- Absolute path for the file.
    """

    def __init__(self, day, month, year, path, station='Sagamore Hill'):
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
        if os.path.exists(self._path):
            print("Path exists")
        else:
            os.mkdir(self._path)
        self._station = station

    def get_filename(self):
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
            file_gzip {bool} -- Sets if the extension will have .gz. (default: {True})

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
            file_gzip {bool} -- Sets if the extension will have .gz. (default: {True})

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
            if (arquivo == filename_upper or
                    arquivo == filename_lower):
                return arquivo

        return False

    def __set_filename(self, upper):
        """Creates the file name.

        Arguments:
            upper {bool} -- Sets if the file is going to be upper case or lower case.

        Returns:
            {str} -- The file's name.
        """

        if upper:
            filename = self._day + self.__change_month_upper() + self._year[2:]
        else:
            filename = self._day + self.__change_month_lower() + self._year[2:]

        return filename

    def __set_url(self, upper, http=True):
        """Creates the url of the file to be downloaded.

        Arguments:
            upper {bool} -- Used to try downloading both name in upper and lower case.

        Keyword Arguments:
            http {bool} -- Sets the url to be http or ftp. (default: {True})

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

        if http:
            url = 'https://ngdc.noaa.gov/stp/space-weather/solar-data/'
        else:
            url = 'ftp://ftp.ngdc.noaa.gov/STP/space-weather/solar-data/'

        url += 'solar-features/solar-radio/rstn-1-second/'
        url += station_name + '/' + self._year + '/' + self._month + '/'
        url += filename + file_extension

        return url

    def download_data_ftp(self):
        """Downloads the file via ftp.

        Returns:
            {bool} -- True when the file was downloaded, False if an error occours.
        """

        try:
            ftp = FTP('ftp.ngdc.noaa.gov')
            print(ftp.getwelcome())
            ftp.login()
        except HTTPError:
            print("Connection not established.")
            return False

        if self.file_exists():
            print("File already downloaded.")
            return False

        # Tries to download with the file extension in upper case.
        # Then tries to download with the file extension in lower case.
        try:
            url = self.__set_url(True, False)
            filename = wget.download(url)
        except HTTPError:
            try:
                url = self.__set_url(False, False)
                filename = wget.download(url)
            except HTTPError:
                filename = "no_data"
        finally:
            self._filename = filename
            return True

    def download_data(self):
        """Downloads the file via https.

        Returns:
            {bool} -- True when the file was downloaded.
        """

        if self.file_exists() is not False:
            print("File already downloaded")
            return self.file_exists()

        # Tries to download with the file extension in upper case.
        # Then tries to download with the file extension in lower case.
        try:
            url = self.__set_url(True)
            print("Downloading {}".format(url))
            filename = wget.download(url)
        except HTTPError:
            try:
                url = self.__set_url(False)
                print("Downloading {}".format(url))
                filename = wget.download(url)
            except HTTPError:
                filename = "no_data"
        finally:
            self._filename = filename
            return True

    def decompress_file(self):
        """It doesn't really decompress the file, it saves the data
        inside in a different file with the same name.

        Returns:
            {str} -- File's final name.
        """

        if self.file_exists() is not False:
            print("File already downloaded")
            return self.file_exists()

        # Checks if the filename variable exists.
        try:
            print(self._filename)
            if self._filename == "no_data":
                print("No file")
                return False
        except AttributeError:
            print("You need to download the file first.")
            return False

        with gzip.open(self._filename, 'rb') as _file:
            file_content = _file.read()
            # Removes .gz from filename.
            final_name = self._filename.split('.gz')
            with open(final_name[0], 'wb') as final_file:
                # Saves the content to a new file.
                final_file.write(file_content)

        try:
            os.rename(final_name[0], self._path + final_name[0])
        except FileExistsError:
            pass

        os.remove(self._filename)
        return final_name[0]
