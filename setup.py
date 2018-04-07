from setuptools import setup


setup(
    name="noaa-ftp",
    version="0.1",
    description="Download solar data from noaa's FTP",
    keywords="noaa ftp solar-data solar sagamore hill san vito",
    url="https://github.com/3ldr0n/noaa-ftp",
    author="Edison Neto and Douglas Silva",
    author_email="ednetoali@gmail.com",
    license="GPLv2",
    packages=['noaa-ftp'],
    install_requires=['wget'],
    zip_safe=False
)

