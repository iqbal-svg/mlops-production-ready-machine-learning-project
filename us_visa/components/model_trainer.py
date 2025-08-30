import sys   # Provides access to system-specific parameters and functions
from typing import Tuple   # Used for type hinting function return types

import numpy as np   # Library for numerical computations
import pandas as pd   # Library for data manipulation and analysis
from pandas import DataFrame   # Explicit import of DataFrame class from pandas
from sklearn.pipeline import Pipeline   # Helps in chaining preprocessing + ML model together
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score  # Classification evaluation metrics
from neuro_mf  import ModelFactory   # Custom AutoML-like tool to select the best model automatically

from us_visa.exception import USvisaException   # Custom exception handling class for project
from us_visa.logger import logging   # Custom logging utility
from us_visa.utils.main_utils import load_numpy_array_data, read_yaml_file, load_object, save_object  
# Utility functions: load numpy arrays, read YAML config files, load & save Python objects

from us_visa.entity.config_entity import ModelTrainerConfig  
# Entity class holding configuration for model training (paths, thresholds, etc.)
from us_visa.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, ClassificationMetricArtifact  
# Entity classes that represent outputs (artifacts) of each ML pipeline stage
from us_visa.entity.estimator import USvisaModel  
# Wrapper class that combines preprocessing object + trained ML model


class ModelTrainer:   # Defines a class responsible for training the ML model
    def __init__(self, data_transformation_artifact: DataTransformationArtifact,
                 model_trainer_config: ModelTrainerConfig):   # Constructor takes in transformation outputs & config
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_transformation_config: Configuration for data transformation
        """
        self.data_transformation_artifact = data_transformation_artifact   # Save artifact info as instance variable
        self.model_trainer_config = model_trainer_config   # Save trainer config as instance variable

    def get_model_object_and_report(self, train: np.array, test: np.array) -> Tuple[object, object]:
        """
        Method Name :   get_model_object_and_report
        Description :   This function uses neuro_mf to get the best model object and report of the best model
        
        Output      :   Returns metric artifact object and best model object
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            logging.info("Using neuro_mf to get best model object and report")  
            # Log the start of model selection process

            model_factory = ModelFactory(model_config_path=self.model_trainer_config.model_config_file_path)  
            # Create ModelFactory object with model config file path (AutoML helper)

            x_train, y_train, x_test, y_test = train[:, :-1], train[:, -1], test[:, :-1], test[:, -1]  
            # Split features and target from train/test numpy arrays

            best_model_detail = model_factory.get_best_model(
                X=x_train,y=y_train,base_accuracy=self.model_trainer_config.expected_accuracy
            )  
            # Get the best ML model using ModelFactory (based on base accuracy threshold)

            model_obj = best_model_detail.best_model  
            # Extract the best model object from details

            y_pred = model_obj.predict(x_test)  
            # Predict labels for test data using best model

            accuracy = accuracy_score(y_test, y_pred)   # Compute accuracy
            f1 = f1_score(y_test, y_pred)   # Compute F1-score
            precision = precision_score(y_test, y_pred)   # Compute precision
            recall = recall_score(y_test, y_pred)   # Compute recall

            metric_artifact = ClassificationMetricArtifact(f1_score=f1, precision_score=precision, recall_score=recall)  
            # Store metrics inside a ClassificationMetricArtifact object

            return best_model_detail, metric_artifact  
            # Return both best model details and classification metrics
        
        except Exception as e:
            raise USvisaException(e, sys) from e   # If error occurs, wrap inside project-specific exception
        

    def initiate_model_trainer(self, ) -> ModelTrainerArtifact:   # Main method to train and save best model
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")  
        # Log entry point of model trainer

        """
        Method Name :   initiate_model_trainer
        Description :   This function initiates a model trainer steps
        
        Output      :   Returns model trainer artifact
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            train_arr = load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_file_path)  
            # Load transformed training data (numpy array)

            test_arr = load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_file_path)  
            # Load transformed testing data (numpy array)
            
            best_model_detail ,metric_artifact = self.get_model_object_and_report(train=train_arr, test=test_arr)  
            # Get best model and metrics using earlier function
            
            preprocessing_obj = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)  
            # Load preprocessing object (scaler, encoder, etc.)

            if best_model_detail.best_score < self.model_trainer_config.expected_accuracy:  
                # If best model score is lower than expected accuracy threshold
                logging.info("No best model found with score more than base score")  
                raise Exception("No best model found with score more than base score")  
                # Raise error since model performance is not acceptable

            usvisa_model = USvisaModel(preprocessing_object=preprocessing_obj,
                                       trained_model_object=best_model_detail.best_model)  
            # Create a custom USvisaModel object that combines preprocessing + model

            logging.info("Created usvisa model object with preprocessor and model")  
            logging.info("Created best model file path.")  

            save_object(self.model_trainer_config.trained_model_file_path, usvisa_model)  
            # Save the trained model object into a file

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                metric_artifact=metric_artifact,
            )  
            # Create ModelTrainerArtifact object that stores model path & metrics

            logging.info(f"Model trainer artifact: {model_trainer_artifact}")  
            # Log final artifact

            return model_trainer_artifact   # Return final artifact containing trained model & metrics

        except Exception as e:
            raise USvisaException(e, sys) from e   # Raise project-specific exception if error occurs