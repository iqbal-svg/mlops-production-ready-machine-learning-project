import json  # Provides functions to work with JSON data (load, dump, parse etc.)
import sys   # Gives access to system-specific parameters and functions (used in exception handling)

import pandas as pd  # Pandas library for data manipulation and analysis
from evidently import Report  # Used to create a data drift profile report
from evidently.presets import DataDriftPreset
from evidently.metrics import ValueDrift # Section of Evidently report specifically for data drift

from pandas import DataFrame  # Importing DataFrame type hint directly for cleaner type annotations

from us_visa.exception import USvisaException  # Custom exception class for handling errors
from us_visa.logger import logging  # Custom logging utility for logging messages
from us_visa.utils.main_utils import read_yaml_file, write_yaml_file  # Helper functions for reading/writing YAML files
from us_visa.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact  # Data classes to store artifacts
from us_visa.entity.config_entity import DataValidationConfig  # Configuration class for data validation
from us_visa.constants import SCHEMA_FILE_PATH  # Constant that stores the schema file path
import os

import json












class DataValidation:  # Class responsible for validating data
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_validation_config: configuration for data validation
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact  # Store ingestion artifact (contains train/test data paths)
            self.data_validation_config = data_validation_config  # Store validation configuration
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)  # Load schema YAML file
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception if error occurs

    def validate_number_of_columns(self, dataframe: DataFrame) -> bool:
        """
        Validates whether the dataframe has the expected number of columns.
        """
        try:
            status = len(dataframe.columns) == len(self._schema_config["columns"])  # Compare dataframe columns with schema columns
            logging.info(f"Is required column present: [{status}]")  # Log validation result
            return status  # Return True/False
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception if error occurs

    def is_column_exist(self, df: DataFrame) -> bool:
        """
        Checks whether required numerical and categorical columns exist in dataframe.
        """
        try:
            dataframe_columns = df.columns  # Get list of dataframe columns
            missing_numerical_columns = []  # Store missing numerical columns
            missing_categorical_columns = []  # Store missing categorical columns

            # Check each numerical column from schema
            for column in self._schema_config["numerical_columns"]:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)  # Add to missing list if not found

            if len(missing_numerical_columns) > 0:  # If missing numerical columns exist
                logging.info(f"Missing numerical column: {missing_numerical_columns}")

            # Check each categorical column from schema
            for column in self._schema_config["categorical_columns"]:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)  # Add to missing list if not found

            if len(missing_categorical_columns) > 0:  # If missing categorical columns exist
                logging.info(f"Missing categorical column: {missing_categorical_columns}")

            # Return True if no missing column, otherwise False
            return False if len(missing_categorical_columns) > 0 or len(missing_numerical_columns) > 0 else True
        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception

    @staticmethod
    def read_data(file_path) -> DataFrame:  # Static method (doesn’t need self)
        try:
            return pd.read_csv(file_path)  # Read CSV file and return dataframe
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception
        

    

    
        
    
    def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame) -> bool:
        try:
            from evidently import Report
            from evidently.presets import DataDriftPreset

            # 1. Create and run the report
            report = Report([DataDriftPreset()])
            eval_result = report.run(current_data=current_df, reference_data=reference_df)

            # 2. Ensure directory exists
            html_path = self.data_validation_config.drift_report_file_path.replace(".yaml", ".html")
            os.makedirs(os.path.dirname(html_path), exist_ok=True)

            # 3. Save HTML report
            eval_result.save_html(html_path)

            # 4. Save dict version in YAML
            report_dict = eval_result.dict()
            write_yaml_file(
                file_path=self.data_validation_config.drift_report_file_path,
                content=report_dict
            )

            #5. Extract drift results
            drift_info = report_dict["metrics"][0]["value"]
            print("drift_info keys:", drift_info.keys())
            #n_features = drift_info["value"].get("number_of_columns", reference_df.shape[1])
            #n_features = drift_info["number_of_columns"]
            n_drifted = drift_info.get("count", 0)
            share_drifted = drift_info.get("share", 0)
            n_features = reference_df.shape[1]

            print(f"Drifted columns: {n_drifted}/{n_features}, Share: {share_drifted}")
            n_drifted_features = drift_info.get("count", 0)
            dataset_drift = (drift_info.get("share", 0.0) > 0.3)

            logging.info(f"{n_drifted_features}/{n_features} features show drift.")
            return dataset_drift
        
            

        except Exception as e:
            raise USvisaException(e, sys) from e
    
    # def detect_dataset_drift(self, reference_df: DataFrame, current_df: DataFrame) -> bool:
    #     """
    #     Detects dataset drift between reference (train) and current (test) dataframes.
    #     """
    #     try:
    #         #data_drift_profile = Profile(sections=[DataDriftProfileSection()])  # Create profile with drift section
    #         data_drift_report = Report(metrics=[DataDriftPreset()])
    #         ValueDrift.calculate(reference_df, current_df)  # Compare train vs test data

    #         report = ValueDrift.json()  # Get report in JSON format
    #         json_report = json.loads(report)  # Convert JSON string to dictionary

    #         write_yaml_file(file_path=self.data_validation_config.drift_report_file_path, content=json_report)  
    #         # Save drift report to YAML file

    #         n_features = json_report["data_drift"]["data"]["metrics"]["n_features"]  # Total number of features
    #         n_drifted_features = json_report["data_drift"]["data"]["metrics"]["n_drifted_features"]  # Number of drifted features

    #         logging.info(f"{n_drifted_features}/{n_features} drift detected.")  # Log drift results
    #         drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]  # Boolean drift status
    #         return drift_status  # Return True if drift, else False
    #     except Exception as e:
    #         raise USvisaException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Orchestrates full data validation process (columns + drift check).
        """
        try:
            validation_error_msg = ""  # Store validation error messages
            logging.info("Starting data validation")  # Log start of validation

            # Load train and test datasets
            train_df, test_df = (DataValidation.read_data(file_path=self.data_ingestion_artifact.trained_file_path),
                                 DataValidation.read_data(file_path=self.data_ingestion_artifact.test_file_path))

            # Validate column count for train
            status = self.validate_number_of_columns(dataframe=train_df)
            logging.info(f"All required columns present in training dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."

            # Validate column count for test
            status = self.validate_number_of_columns(dataframe=test_df)
            logging.info(f"All required columns present in testing dataframe: {status}")
            if not status:
                validation_error_msg += f"Columns are missing in test dataframe."

            # Validate column existence for train
            status = self.is_column_exist(df=train_df)
            if not status:
                validation_error_msg += f"Columns are missing in training dataframe."

            # Validate column existence for test
            status = self.is_column_exist(df=test_df)
            if not status:
                validation_error_msg += f"columns are missing in test dataframe."

            # If no column errors, check drift
            validation_status = len(validation_error_msg) == 0
            if validation_status:
                drift_status = self.detect_dataset_drift(train_df, test_df)  # Perform drift detection
                if drift_status:
                    logging.info(f"Drift detected.")
                    validation_error_msg = "Drift detected"  # Update message if drift exists
                else:
                    validation_error_msg = "Drift not detected"  # Update message if no drift
            else:
                logging.info(f"Validation_error: {validation_error_msg}")  # Log error if validation failed

            # Create artifact object with validation results
            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,  # True if validation passed
                message=validation_error_msg,  # Error or drift message
                drift_report_file_path=self.data_validation_config.drift_report_file_path  # Path to drift report
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")  # Log artifact details
            return data_validation_artifact  # Return validation artifact
        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception