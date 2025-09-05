import os  # Provides functions to interact with the operating system (e.g., file paths, directories)
import sys  # Provides access to Python runtime environment (used here for exception handling)

import numpy as np  # Numerical computing library, useful for arrays, math operations
import pandas as pd  # Data analysis library, mainly for working with DataFrames
from us_visa.entity.config_entity import USvisaPredictorConfig  # Imports configuration class for prediction
from us_visa.entity.s3_estimator import USvisaEstimator  # Imports estimator class that loads model from S3 and predicts
from us_visa.exception import USvisaException  # Custom exception class for consistent error handling
from us_visa.logger import logging  # Custom logging utility to log messages
from us_visa.utils.main_utils import read_yaml_file  # Utility function to read YAML config files
from pandas import DataFrame  # Direct import of pandas DataFrame class


class USvisaData:  # Class to handle input features for US visa prediction
    def __init__(self,
                continent,  # Continent of employee’s origin
                education_of_employee,  # Education level of employee
                has_job_experience,  # Whether employee has job experience (Yes/No)
                requires_job_training,  # Whether job requires training (Yes/No)
                no_of_employees,  # Number of employees in the company
                region_of_employment,  # Geographic region of employment
                prevailing_wage,  # Employee’s wage
                unit_of_wage,  # Unit of wage (Yearly, Hourly, etc.)
                full_time_position,  # Whether job is full-time (Y/N)
                company_age  # Age of the company
                ):
        """
        USvisa Data constructor
        Input: all features of the trained model for prediction
        """
        try:
            # Assigning all input parameters to class variables
            self.continent = continent  
            self.education_of_employee = education_of_employee
            self.has_job_experience = has_job_experience
            self.requires_job_training = requires_job_training
            self.no_of_employees = no_of_employees
            self.region_of_employment = region_of_employment
            self.prevailing_wage = prevailing_wage
            self.unit_of_wage = unit_of_wage
            self.full_time_position = full_time_position
            self.company_age = company_age

        except Exception as e:  # Catch any exception while initializing
            raise USvisaException(e, sys) from e  # Raise custom exception with system info

    def get_usvisa_input_data_frame(self) -> DataFrame:
        """
        This function returns a DataFrame from USvisaData class input
        """
        try:
            # Convert input data into dictionary format
            usvisa_input_dict = self.get_usvisa_data_as_dict()  
            # Convert dictionary into pandas DataFrame
            return DataFrame(usvisa_input_dict)  

        except Exception as e:  # Handle exceptions
            raise USvisaException(e, sys) from e  

    def get_usvisa_data_as_dict(self):
        """
        This function returns a dictionary from USvisaData class input 
        """
        logging.info("Entered get_usvisa_data_as_dict method as USvisaData class")  # Log entry message

        try:
            # Create dictionary with each feature as key and its value inside a list
            input_data = {
                "continent": [self.continent],
                "education_of_employee": [self.education_of_employee],
                "has_job_experience": [self.has_job_experience],
                "requires_job_training": [self.requires_job_training],
                "no_of_employees": [self.no_of_employees],
                "region_of_employment": [self.region_of_employment],
                "prevailing_wage": [self.prevailing_wage],
                "unit_of_wage": [self.unit_of_wage],
                "full_time_position": [self.full_time_position],
                "company_age": [self.company_age],
            }

            logging.info("Created usvisa data dict")  # Log that dictionary is created
            logging.info("Exited get_usvisa_data_as_dict method as USvisaData class")  # Log exit message

            return input_data  # Return dictionary

        except Exception as e:  # Catch errors in dict creation
            raise USvisaException(e, sys) from e  # Raise custom exception


class USvisaClassifier:  # Class that uses trained model to predict
    def __init__(self, prediction_pipeline_config: USvisaPredictorConfig = USvisaPredictorConfig(),) -> None:
        """
        :param prediction_pipeline_config: Configuration for prediction the value
        """
        try:
            # Store configuration (contains S3 bucket name and model path)
            self.prediction_pipeline_config = prediction_pipeline_config
        except Exception as e:  # Catch error if config fails
            raise USvisaException(e, sys)

    def predict(self, dataframe) -> str:
        """
        This is the method of USvisaClassifier
        Returns: Prediction in string format
        """
        try:
            logging.info("Entered predict method of USvisaClassifier class")  # Log entry message
            # Load trained model from S3 using USvisaEstimator
            model = USvisaEstimator(
                bucket_name=self.prediction_pipeline_config.model_bucket_name,
                model_path=self.prediction_pipeline_config.model_file_path,
            )
            # Make prediction using the model
            result = model.predict(dataframe)  
            
            return result  # Return prediction result
        
        except Exception as e:  # Catch any error during prediction
            raise USvisaException(e, sys)  # Raise custom exception