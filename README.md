# GetRSTN

Download RSTN 1 second data from NOAA's site. Working for data after 2000.

## Installation

```bash
pip install getrstn
```

## How to use it

```python
import matplotlib.pyplot as plt

from getrstn import GetRSTN

day = 16
month = 10
year = 2014
path_to_files = "data/"
station = "San vito"

rstn = GetRSTN(day, month, year, path_to_files, station)

# Downloads, decompress the file and generate a dataframe.
rstn.download_file()
filename = rstn.decompress_file()
df = rstn.create_dataframe()

# Plots the data.
ax = rstn.plot()
plt.plot()
```

## Compatibility

The library was tested with Python 3, and Python 2.7.
