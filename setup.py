from setuptools import setup

with open("README.org", "r") as readme:
    long_description = readme.read()

setup(
    name="rstnpy",
    version="1.0",
    author="Edison Neto",
    author_email="ednetoali@gmail.com",
    description="Library used to work with rstn-1-second data",
    long_description=long_description,
    url="https://github.com/craam/rstnpy",
    packages=['rstnpy'],
    include_package_data=True,
    install_requires=[
        'requests>=2.20',
        'numpy>=1.13',
        'pandas>=0.21'
        'matplotlib>=2.2.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
)
