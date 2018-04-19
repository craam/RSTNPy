# noaa-ftp
Download solar data from noaa's ftp.

## How to use it

```python
from noaaftp import NoaaFTP

day = 9
month = 4
year = 2002
station = "Sagamore Hill"

noaa = NoaaFTP(day, month, year, station)
noaa.download_data()
noaa.decompress_file()
```
