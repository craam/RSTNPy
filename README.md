# noaa-ftp
Download solar data from noaa's ftp.

## How to use it

```python
noaa = NoaaFTP(day, month, year, station)
noaa.download_data()
noaa.decompress_file()
```
