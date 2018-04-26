# noaaftp
Download solar data from noaa's ftp.

## How to use it

```python
from noaaftp import NoaaFTP

day = 9
month = 4
year = 2002
path_to_files = "data/"
station = "Sagamore Hill"

noaa = NoaaFTP(day, month, year, path_to_files, station)
noaa.download_data()
noaa.decompress_file()
```
