from setuptools import setup, find_packages  # Importing 'setup' and 'find_packages' from setuptools to configure the package and automatically find sub-packages

setup(  # Calling the 'setup' function to define the package metadata and configuration
    name="us_visa",  # The name of the package (used when installing via pip)
    version="0.0.0",  # Version number of the package, useful for tracking changes and updates
    author="iqbal",  # Name of the package author
    author_email="iqbalshaikhsap@gmail.com",  # Email address of the author
    packages=find_packages()  # Automatically find and include all packages (folders with __init__.py) in the project
)