from us_visa.configuration.mongo_db_connection import MongoDBClient  # Importing MongoDBClient class to handle MongoDB connection
from us_visa.constants import DATABASE_NAME  # Importing the database name constant
from us_visa.exception import USvisaException  # Custom exception class for error handling
import pandas as pd  # Importing pandas for data handling and DataFrame creation
import sys  # Provides system-specific functions (used here for exception details)
from typing import Optional  # Allows specifying optional parameters in function signatures
import numpy as np  # Importing numpy (used here for handling NaN values)


class USvisaData:
    """
    This class helps to export entire MongoDB record as a pandas DataFrame
    """

    def __init__(self):
        """
        Constructor: Initializes MongoDB client connection
        """
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)  # Create MongoDB client object connected to given DB
        except Exception as e:  # Catch any exception while connecting
            raise USvisaException(e, sys)  # Raise custom exception with error and system info
        

    def export_collection_as_dataframe(self, collection_name: str, database_name: Optional[str] = None) -> pd.DataFrame:
        try:
            """
            Export entire MongoDB collection as pandas DataFrame.
            Returns: DataFrame containing collection records.
            """
            if database_name is None:  # If no database is provided, use the default one
                collection = self.mongo_client.database[collection_name]  # Access collection from default DB
            else:
                collection = self.mongo_client[database_name][collection_name]  # Access collection from given DB

            df = pd.DataFrame(list(collection.find()))  # Fetch all documents from collection and convert into DataFrame

            if "_id" in df.columns.to_list():  # If MongoDB’s default "_id" column exists
                df = df.drop(columns=["_id"], axis=1)  # Drop it since it’s usually not needed for analysis

            df.replace({"na": np.nan}, inplace=True)  # Replace string "na" with numpy NaN for missing values

            return df  # Return the cleaned DataFrame
        except Exception as e:  # If any error occurs while fetching/exporting
            raise USvisaException(e, sys)  # Raise custom exception