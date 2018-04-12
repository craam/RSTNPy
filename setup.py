from setuptools import setup


setup(
    name="noaa-ftp",
    version="0.1",
    url="https://github.com/3ldr0n/noaa-ftp",
    author="Edison Neto and Douglas Silva",
    author_email="ednetoali@gmail.com",
    license="GPLv2",
    packages=['noaa-ftp'],
    include_package_data=True,
    install_requires=['wget']
)

