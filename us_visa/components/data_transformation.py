import sys  # Provides access to system-specific parameters and functions (like sys.exit, sys.path, etc.)

import numpy as np  # Library for numerical operations (arrays, linear algebra, etc.)
import pandas as pd  # Library for working with tabular data (DataFrames, Series)

from imblearn.combine import SMOTEENN  # Technique for handling imbalanced datasets (combines SMOTE oversampling + ENN undersampling)

from sklearn.pipeline import Pipeline  # Used to build ML pipelines (sequential steps of preprocessing + modeling)
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, PowerTransformer  
# - StandardScaler: scales numerical features to mean=0 and variance=1  
# - OneHotEncoder: converts categorical features into binary columns (dummy variables)  
# - OrdinalEncoder: converts categorical values into integer codes (for ordered categories)  
# - PowerTransformer: transforms features to be more Gaussian-like (helps stabilize variance & normalize distribution)

from sklearn.compose import ColumnTransformer  
# Allows applying different preprocessing (scaling, encoding, etc.) to different columns of a DataFrame

from us_visa.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR  
# Imports project-specific constants:  
# - TARGET_COLUMN → name of the target variable (label)  
# - SCHEMA_FILE_PATH → path to the schema YAML file (defines dataset structure)  
# - CURRENT_YEAR → likely used for feature engineering (like calculating applicant’s age or year differences)

from us_visa.entity.config_entity import DataTransformationConfig  
# Configuration class for Data Transformation (stores settings like paths, parameters, etc.)

from us_visa.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact  
# Artifact classes → objects used to pass processed results between pipeline stages (e.g., ingestion, validation, transformation)

from us_visa.exception import USvisaException  
# Custom exception class for handling errors in the US Visa ML project

from us_visa.logger import logging  
# Project-specific logging utility for recording info, warnings, and errors

from us_visa.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file, drop_columns  
# Utility functions:  
# - save_object → saves Python objects (e.g., models, transformers) as pickle files  
# - save_numpy_array_data → saves NumPy arrays to disk  
# - read_yaml_file → reads YAML configuration files (like schema)  
# - drop_columns → removes unnecessary columns from DataFrame

from us_visa.entity.estimator import TargetValueMapping  
# Class for mapping target variable values (e.g., {"Approved": 1, "Denied": 0}) for ML modeling

class DataTransformation:   # Defines a class to handle all data transformation steps
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):  # Constructor method with required artifacts and configs
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_transformation_config: configuration for data transformation
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact  # Save ingestion artifact object
            self.data_transformation_config = data_transformation_config  # Save transformation config object
            self.data_validation_artifact = data_validation_artifact  # Save validation artifact object
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)  # Load schema details (columns info) from YAML
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception if initialization fails

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:  # Static method to read CSV data into pandas DataFrame
        try:
            return pd.read_csv(file_path)  # Read CSV file from given path
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception if reading fails

    
    def get_data_transformer_object(self) -> Pipeline:  # Method to create and return preprocessing pipeline
        """
        Method Name :   get_data_transformer_object
        Description :   This method creates and returns a data transformer object for the data
        """
        logging.info("Entered get_data_transformer_object method of DataTransformation class")  # Log entry

        try:
            numeric_transformer = StandardScaler()  # Scale numerical columns
            oh_transformer = OneHotEncoder()  # Encode categorical columns into one-hot vectors
            ordinal_encoder = OrdinalEncoder()  # Encode ordinal columns into integer labels

            logging.info("Initialized StandardScaler, OneHotEncoder, OrdinalEncoder")  # Log status

            oh_columns = self._schema_config['oh_columns']  # Get one-hot columns from schema
            or_columns = self._schema_config['or_columns']  # Get ordinal columns from schema
            transform_columns = self._schema_config['transform_columns']  # Get columns to apply PowerTransformer
            num_features = self._schema_config['num_features']  # Get numeric columns from schema

            logging.info("Initialize PowerTransformer")  # Log status

            transform_pipe = Pipeline(steps=[
                ('transformer', PowerTransformer(method='yeo-johnson'))  # Handle skewness in data
            ])
            
            preprocessor = ColumnTransformer(  # Combine all preprocessing steps
                [
                    ("OneHotEncoder", oh_transformer, oh_columns),  # One-hot encode categorical cols
                    ("Ordinal_Encoder", ordinal_encoder, or_columns),  # Ordinal encode categorical cols
                    ("Transformer", transform_pipe, transform_columns),  # Apply power transform
                    ("StandardScaler", numeric_transformer, num_features)  # Scale numeric cols
                ]
            )

            logging.info("Created preprocessor object from ColumnTransformer")  # Log success
            logging.info("Exited get_data_transformer_object method of DataTransformation class")  # Log exit
            return preprocessor  # Return preprocessor object

        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception on error

    def initiate_data_transformation(self, ) -> DataTransformationArtifact:  # Main method to perform transformation
        """
        Initiates data transformation: preprocessing + feature engineering + imbalance handling
        """
        try:
            if self.data_validation_artifact.validation_status:  # Proceed only if validation is successful
                logging.info("Starting data transformation")  # Log start

                preprocessor = self.get_data_transformer_object()  # Get preprocessing object
                logging.info("Got the preprocessor object")  # Log success

                train_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)  # Read train CSV
                test_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.test_file_path)  # Read test CSV

                input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)  # Separate train features
                target_feature_train_df = train_df[TARGET_COLUMN]  # Separate train target
                logging.info("Got train features and test features of Training dataset")  # Log status

                input_feature_train_df['company_age'] = CURRENT_YEAR - input_feature_train_df['yr_of_estab']  # Feature engineering
                logging.info("Added company_age column to the Training dataset")  # Log status

                drop_cols = self._schema_config['drop_columns']  # Get drop columns from schema
                input_feature_train_df = drop_columns(df=input_feature_train_df, cols=drop_cols)  # Drop unwanted cols
                logging.info("drop the columns in drop_cols of Training dataset")  # Log status
                
                target_feature_train_df = target_feature_train_df.replace(
                    TargetValueMapping()._asdict()  # Map target values (like Yes/No to 1/0)
                )

                input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)  # Separate test features
                target_feature_test_df = test_df[TARGET_COLUMN]  # Separate test target

                input_feature_test_df['company_age'] = CURRENT_YEAR - input_feature_test_df['yr_of_estab']  # Feature engineering
                logging.info("Added company_age column to the Test dataset")  # Log status

                input_feature_test_df = drop_columns(df=input_feature_test_df, cols=drop_cols)  # Drop unwanted cols
                logging.info("drop the columns in drop_cols of Test dataset")  # Log status

                target_feature_test_df = target_feature_test_df.replace(
                TargetValueMapping()._asdict()  # Map test target values
                )

                logging.info("Got train features and test features of Testing dataset")  # Log status

                input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)  # Fit-transform train data
                logging.info("Used the preprocessor object to fit transform the train features")  # Log status

                input_feature_test_arr = preprocessor.transform(input_feature_test_df)  # Transform test data
                logging.info("Used the preprocessor object to transform the test features")  # Log status

                logging.info("Applying SMOTEENN on Training dataset")  # Log balancing
                smt = SMOTEENN(sampling_strategy="minority")  # Initialize SMOTEENN

                input_feature_train_final, target_feature_train_final = smt.fit_resample(
                    input_feature_train_arr, target_feature_train_df  # Balance training dataset
                )
                logging.info("Applied SMOTEENN on training dataset")  # Log success

                logging.info("Applying SMOTEENN on testing dataset")  # Log balancing
                input_feature_test_final, target_feature_test_final = smt.fit_resample(
                    input_feature_test_arr, target_feature_test_df  # Balance testing dataset
                )
                logging.info("Applied SMOTEENN on testing dataset")  # Log success

                train_arr = np.c_[input_feature_train_final, np.array(target_feature_train_final)]  # Combine X and y (train),saving in numpy frmt
                test_arr = np.c_[input_feature_test_final, np.array(target_feature_test_final)]  # Combine X and y (test),saving in numpy frmt
                logging.info("Created train array and test array")  # Log success

                save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)  # Save preprocessor
                save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)  # Save train
                save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)  # Save test
                logging.info("Saved the preprocessor object")  # Log success

                logging.info("Exited initiate_data_transformation method of Data_Transformation class")  # Log exit

                data_transformation_artifact = DataTransformationArtifact(
                    transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,  # Path to preprocessor
                    transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,  # Path to transformed train
                    transformed_test_file_path=self.data_transformation_config.transformed_test_file_path  # Path to transformed test
                )
                return data_transformation_artifact  # Return artifact object
            else:
                raise Exception(self.data_validation_artifact.message)  # Raise error if validation failed

        except Exception as e:
            raise USvisaException(e, sys) from e  # Custom exception handling