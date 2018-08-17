from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="getrstn",
    version="0.3.2",
    author="Edison Neto and Douglas Silva",
    author_email="ednetoali@gmail.com",
    description="Downloads rstn-1-second data",
    long_description=long_description,
    url="https://github.com/3ldr0n/getrstn",
    packages=['getrstn'],
    include_package_data=True,
    install_requires=[
        'wget>=3.2',
        'numpy>=1.13',
        'pandas>=0.21'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
)
