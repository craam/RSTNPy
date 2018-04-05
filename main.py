import gzip
from ftplib import FTP

class NoaaFTP:

    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

    
    def download_data(self):
        ftp = FTP('ftp.ngdc.noaa.gov')
        ftp.login() 
        
        ftp.dir()
        ftp.cwd('STP/space-weather/solar-data/solar-features/solar-radio/rstn-1-second')
        
        ftp.cwd('sagamore-hill/2002/09')
        
        ftp.retrbinary('RETR 04SEP02.K7O.gz', open('04SEP02.K7O.gz', 'wb').write)
        
        ftp.quit()

    def decompress_file(self):
        gzip.GzipFile(self.filename)

        with gzip.open('04SEP02.K70.gz', 'rb') as _file:
            file_content = _file.read()
            print file_content
