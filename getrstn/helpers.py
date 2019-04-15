import numpy as np


def format_day(self, day):
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


def format_month(self, month):
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


def format_station_for_url(self, station):
    """Formats the station name as it is in NOAA's site for the url.

    Returns
    -------
    str
        The station name as it is in the site url.

    """

    return station.lower().replace(' ', '-')


def cast_to_int64(self, number):
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
