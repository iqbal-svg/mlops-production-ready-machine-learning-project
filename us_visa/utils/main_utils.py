import os  # Provides functions to interact with the operating system (e.g., paths, directories, files)
import sys  # Provides access to system-specific parameters and functions (used for exception handling)

import numpy as np  # NumPy for numerical operations and arrays
import dill  # dill for serializing Python objects (more flexible than pickle)
import yaml  # For reading and writing YAML files
from pandas import DataFrame  # Import DataFrame type hint from pandas

from us_visa.exception import USvisaException  # Custom exception class for consistent error handling
from us_visa.logger import logging  # Custom logger for logging messages


def read_yaml_file(file_path: str) -> dict:  # Reads YAML file and returns its contents as a dictionary
    try:
        with open(file_path, "rb") as yaml_file:  # Open the file in binary read mode
            return yaml.safe_load(yaml_file)  # Parse YAML content into a Python dictionary

    except Exception as e:  # If an error occurs while reading/parsing
        raise USvisaException(e, sys) from e  # Raise custom exception with detailed info
    


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:  
    # Writes a Python object to a YAML file, replacing it if 'replace' is True
    try:
        if replace:  # If replace option is True
            if os.path.exists(file_path):  # Check if file exists
                os.remove(file_path)  # Delete the existing file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure target directory exists
        with open(file_path, "w") as file:  # Open file in write mode
            yaml.dump(content, file)  # Write the Python object to YAML format
    except Exception as e:
        raise USvisaException(e, sys) from e  # Handle errors with custom exception
    


def load_object(file_path: str) -> object:  # Loads a serialized Python object from file
    logging.info("Entered the load_object method of utils")  # Log method entry

    try:
        with open(file_path, "rb") as file_obj:  # Open file in binary read mode
            obj = dill.load(file_obj)  # Deserialize object using dill

        logging.info("Exited the load_object method of utils")  # Log method exit

        return obj  # Return the loaded object

    except Exception as e:
        raise USvisaException(e, sys) from e  # Handle errors with custom exception
    


def save_numpy_array_data(file_path: str, array: np.array):  
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)  # Get directory path from file path
        os.makedirs(dir_path, exist_ok=True)  # Create directory if it doesn't exist
        with open(file_path, 'wb') as file_obj:  # Open file in binary write mode
            np.save(file_obj, array)  # Save NumPy array to file
    except Exception as e:
        raise USvisaException(e, sys) from e  # Handle errors with custom exception
    


def load_numpy_array_data(file_path: str) -> np.array:  
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, 'rb') as file_obj:  # Open file in binary read mode
            return np.load(file_obj)  # Load and return NumPy array
    except Exception as e:
        raise USvisaException(e, sys) from e  # Handle errors with custom exception



def save_object(file_path: str, obj: object) -> None:  # Saves a Python object to file
    logging.info("Entered the save_object method of utils")  # Log method entry

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directory if needed
        with open(file_path, "wb") as file_obj:  # Open file in binary write mode
            dill.dump(obj, file_obj)  # Serialize object using dill

        logging.info("Exited the save_object method of utils")  # Log method exit

    except Exception as e:
        raise USvisaException(e, sys) from e  # Handle errors with custom exception



def drop_columns(df: DataFrame, cols: list) -> DataFrame:  
    """
    drop the columns from a pandas DataFrame
    df: pandas DataFrame
    cols: list of columns to be dropped
    """
    logging.info("Entered drop_columns method of utils")  # Log method entry

    try:
        df = df.drop(columns=cols, axis=1)  # Drop specified columns from DataFrame

        logging.info("Exited the drop_columns method of utils")  # Log method exit
        
        return df  # Return DataFrame after dropping columns
    except Exception as e:
        raise USvisaException(e, sys) from e  # Handle errors with custom exception