# GetRSTN

Download RSTN 1 second data from NOAA's site. 

## Installation

```bash
pip install getrstn
```

## How to use it

```python
import matplotlib.pyplot as plt

from getrstn import GetRSTN

day = 9
month = 4
year = 2002
path_to_files = "data/"
station = "San vito"

rstn = GetRSTN(day, month, year, path_to_files, station)

# Downloads and decompress the file.
rstn.get_file_content()
df = rstn.create_dataframe()

# Plots the data.
ax = rstn.plot()
plt.plot()
```

## Compatibility

The library was tested with Python 3.6, and Python 2.7.14. It'll probably work with other python3 versions, but i don't know if it'll work with Python 2.6 or older versions.
