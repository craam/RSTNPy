# GetRSTN
Download RSTN's data from noaa's site. 

## How to use it

```python
from getrstn import GetRSTN

day = 9
month = 4
year = 2002
path_to_files = "data/"
station = "Sagamore Hill"

noaa = GetRSTN(day, month, year, path_to_files, station)

# Via HTTPS (recommended)
noaa.download_data()
noaa.decompress_file()

# Via FTP.
noaa.download_data()
noaa.decompress_file()
```
