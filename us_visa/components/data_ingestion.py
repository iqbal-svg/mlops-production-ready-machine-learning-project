import os  # Provides functions to interact with the operating system (e.g., creating directories, working with file paths)
import sys  # Provides access to system-specific parameters and functions (also used for exception handling)

from pandas import DataFrame  # Importing DataFrame class from pandas for handling tabular data
from sklearn.model_selection import train_test_split  # Function to split dataset into training and testing sets

from us_visa.entity.config_entity import DataIngestionConfig  # Importing configuration class for data ingestion (contains file paths, ratios, etc.)
from us_visa.entity.artifact_entity import DataIngestionArtifact  # Importing artifact class to store outputs of data ingestion
from us_visa.exception import USvisaException  # Custom exception class for handling project-specific errors
from us_visa.logger import logging  # Custom logging utility to record logs
from us_visa.data_access.usvisa_data import USvisaData  # Class to fetch data from MongoDB


class DataIngestion:  # Class to manage data ingestion (fetching, storing, splitting data)
    def __init__(self,data_ingestion_config:DataIngestionConfig=DataIngestionConfig()):  
        # Constructor method: initializes DataIngestion object with configuration
        try:
            self.data_ingestion_config = data_ingestion_config  # Stores the passed configuration object
        except Exception as e:
            raise USvisaException(e,sys)  # Raises custom exception if initialization fails
        

    def export_data_into_feature_store(self)->DataFrame:  
        """
        Method Name :   export_data_into_feature_store
        Description :   This method exports data from mongodb to csv file
        Output      :   data is returned as artifact of data ingestion components
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            logging.info(f"Exporting data from mongodb")  # Log the start of data export process
            usvisa_data = USvisaData()  # Create object to fetch data from MongoDB
            dataframe = usvisa_data.export_collection_as_dataframe(collection_name=
                                                                   self.data_ingestion_config.collection_name)  
            # Fetch data from MongoDB collection into pandas DataFrame

            logging.info(f"Shape of dataframe: {dataframe.shape}")  # Log the shape (rows, columns) of dataframe
            feature_store_file_path  = self.data_ingestion_config.feature_store_file_path  
            # Get path where feature store file (CSV) will be saved
            dir_path = os.path.dirname(feature_store_file_path)  
            # Get the directory part of the feature store path
            os.makedirs(dir_path,exist_ok=True)  
            # Create directory if it doesn’t exist
            logging.info(f"Saving exported data into feature store file path: {feature_store_file_path}")  
            dataframe.to_csv(feature_store_file_path,index=False,header=True)  
            # Save DataFrame as CSV file in feature store path
            return dataframe  # Return the dataframe

        except Exception as e:
            raise USvisaException(e,sys)  # Raise custom exception if any error occurs
        

    def split_data_as_train_test(self,dataframe: DataFrame) ->None:  
        """
        Method Name :   split_data_as_train_test
        Description :   This method splits the dataframe into train set and test set based on split ratio 
        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info("Entered split_data_as_train_test method of Data_Ingestion class")  
        # Log entry into this method

        try:
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio)  
            # Split the dataframe into training and testing sets based on ratio from config
            logging.info("Performed train test split on the dataframe")  
            logging.info("Exited split_data_as_train_test method of Data_Ingestion class")  

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)  
            # Get directory for training file path
            os.makedirs(dir_path,exist_ok=True)  
            # Create directory if it doesn’t exist
            
            logging.info(f"Exporting train and test file path.")  
            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)  
            # Save training dataset to CSV
            test_set.to_csv(self.data_ingestion_config.testing_file_path,index=False,header=True)  
            # Save testing dataset to CSV

            logging.info(f"Exported train and test file path.")  
        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception if error occurs
        


    def initiate_data_ingestion(self) ->DataIngestionArtifact:  
        """
        Method Name :   initiate_data_ingestion
        Description :   This method initiates the data ingestion components of training pipeline 
        Output      :   train set and test set are returned as the artifacts of data ingestion components
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info("Entered initiate_data_ingestion method of Data_Ingestion class")  
        # Log entry into this method

        try:
            dataframe = self.export_data_into_feature_store()  
            # Step 1: Fetch data from MongoDB and save to feature store CSV

            logging.info("Got the data from mongodb")  

            self.split_data_as_train_test(dataframe)  
            # Step 2: Split dataset into train and test sets

            logging.info("Performed train test split on the dataset")  

            logging.info("Exited initiate_data_ingestion method of Data_Ingestion class")  

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )  
            # Step 3: Create DataIngestionArtifact object with paths of train & test CSV files
            
            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")  
            return data_ingestion_artifact  # Return artifact containing train and test file paths
        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception if error occurs