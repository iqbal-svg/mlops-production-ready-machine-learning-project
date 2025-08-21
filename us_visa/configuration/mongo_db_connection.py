import sys  # Importing sys module (used to get system-specific parameters and functions, also useful for exception handling)

from us_visa.exception import USvisaException  # Importing a custom exception class for handling project-specific errors
from us_visa.logger import logging  # Importing a custom logging utility for recording logs

import os  # Importing os module to access environment variables and file paths
from us_visa.constants import DATABASE_NAME, MONGODB_URL_KEY  # Importing constants like default database name and MongoDB URL key
import pymongo  # Importing pymongo library to connect and interact with MongoDB
import certifi  # Importing certifi to provide trusted CA certificates for SSL/TLS connections

ca = certifi.where()  # Getting the path to the certificate file (used to establish secure MongoDB connection)


class MongoDBClient:  # Defining a class that manages MongoDB connections
    """
    Class Name :   export_data_into_feature_store
    Description :   This method exports the dataframe from mongodb feature store as dataframe 
    
    Output      :   connection to mongodb database
    On Failure  :   raises an exception
    """
    client = None  # A class-level variable to hold the MongoDB client (shared across all instances)

    def __init__(self, database_name=DATABASE_NAME) -> None:  # Constructor to initialize MongoDB connection (default DB from constants)
        try:
            if MongoDBClient.client is None:  # Check if the client is not already created (Singleton pattern)
                mongo_db_url = os.getenv(MONGODB_URL_KEY)  # Get MongoDB URL from environment variables
                if mongo_db_url is None:  # If environment variable is not set
                    raise Exception(f"Environment key: {MONGODB_URL_KEY} is not set.")  # Raise an exception
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)  
                # Create a MongoDB client with secure connection using the certificate file
            self.client = MongoDBClient.client  # Assign the client to the instance variable
            self.database = self.client[database_name]  # Get the reference to the specified database
            self.database_name = database_name  # Store database name in instance variable
            logging.info("MongoDB connection succesfull")  # Log success message
        except Exception as e:  # If any error occurs during connection
            raise USvisaException(e, sys)  # Raise a custom exception with error details and system info