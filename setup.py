from setuptools import setup

setup(
    name="noaaftp",
    version="0.1",
    author="Edison Neto and Douglas Silva",
    author_email="ednetoali@gmail.com",
    packages=['noaaftp'],
    include_package_data=True,
    install_requires=[
        'wget'
    ],
)
