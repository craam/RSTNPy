from setuptools import setup

setup(
    name="getrstn",
    version="0.2.1",
    author="Edison Neto and Douglas Silva",
    author_email="ednetoali@gmail.com",
    packages=['getrstn'],
    include_package_data=True,
    install_requires=[
        'wget'
    ],
)
