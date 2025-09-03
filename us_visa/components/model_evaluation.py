from us_visa.entity.config_entity import ModelEvaluationConfig  # Importing configuration entity for model evaluation
from us_visa.entity.artifact_entity import ModelTrainerArtifact, DataIngestionArtifact, ModelEvaluationArtifact  # Importing required artifact entities
from sklearn.metrics import f1_score  # Importing F1 score metric for evaluation
from us_visa.exception import USvisaException  # Custom exception handling class
from us_visa.constants import TARGET_COLUMN, CURRENT_YEAR  # Importing constants like target column name and current year
from us_visa.logger import logging  # Importing custom logger
import sys  # Importing sys for exception trace
import pandas as pd  # Pandas for data handling
from typing import Optional  # For optional return type hinting
from us_visa.entity.s3_estimator import USvisaEstimator  # Estimator class for interacting with S3 models
from dataclasses import dataclass  # Used to create data classes
from us_visa.entity.estimator import USvisaModel  # Custom trained model class
from us_visa.entity.estimator import TargetValueMapping  # Mapping class to map target labels to numerical values


@dataclass
class EvaluateModelResponse:  # A dataclass to hold evaluation response values
    trained_model_f1_score: float  # F1 score of newly trained model
    best_model_f1_score: float  # F1 score of best/production model
    is_model_accepted: bool  # Whether the new model is better and should be accepted
    difference: float  # Difference in F1 score between new and old model


class ModelEvaluation:  # Class to handle the complete evaluation process

    def __init__(self, model_eval_config: ModelEvaluationConfig, data_ingestion_artifact: DataIngestionArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):  # Constructor with config and artifacts
        try:
            self.model_eval_config = model_eval_config  # Store model evaluation config
            self.data_ingestion_artifact = data_ingestion_artifact  # Store data ingestion artifact
            self.model_trainer_artifact = model_trainer_artifact  # Store trained model artifact
        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception if initialization fails

    def get_best_model(self) -> Optional[USvisaEstimator]:  # Method to fetch best/production model from S3
        """
        Method Name :   get_best_model
        Description :   This function is used to get model in production
        
        Output      :   Returns model object if available in s3 storage
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            bucket_name = self.model_eval_config.bucket_name  # Get S3 bucket name
            model_path = self.model_eval_config.s3_model_key_path  # Get S3 model path
            usvisa_estimator = USvisaEstimator(bucket_name=bucket_name,
                                               model_path=model_path)  # Create estimator object for S3
            
            if usvisa_estimator.is_model_present(model_path=model_path):  # Check if model exists in S3
                return usvisa_estimator  # Return best model if present
            return None  # Otherwise return None
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception on error

    def evaluate_model(self) -> EvaluateModelResponse:  # Method to evaluate newly trained model vs existing production model
        """
        Method Name :   evaluate_model
        Description :   This function is used to evaluate trained model 
                        with production model and choose best model 
        
        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)  # Load test dataset
            test_df['company_age'] = CURRENT_YEAR - test_df['yr_of_estab']  # Create new feature: company age

            x, y = test_df.drop(TARGET_COLUMN, axis=1), test_df[TARGET_COLUMN]  # Separate features (X) and target (Y)
            y = y.replace(
                TargetValueMapping()._asdict()  # Replace target labels with numeric values using mapping
            )

            # trained_model = load_object(file_path=self.model_trainer_artifact.trained_model_file_path)  # Commented: old way of loading model
            trained_model_f1_score = self.model_trainer_artifact.metric_artifact.f1_score  # Get F1 score of trained model from artifact

            best_model_f1_score = None  # Initialize best model F1 score as None
            best_model = self.get_best_model()  # Try fetching best/production model
            if best_model is not None:  # If production model exists
                y_hat_best_model = best_model.predict(x)  # Make predictions using production model
                best_model_f1_score = f1_score(y, y_hat_best_model)  # Calculate its F1 score
            
            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score  # If no production model exists, set score = 0
            result = EvaluateModelResponse(trained_model_f1_score=trained_model_f1_score,
                                           best_model_f1_score=best_model_f1_score,
                                           is_model_accepted=trained_model_f1_score > tmp_best_model_score,  # Accept model if new F1 > old F1
                                           difference=trained_model_f1_score - tmp_best_model_score  # Calculate score difference
                                           )
            logging.info(f"Result: {result}")  # Log the evaluation result
            return result  # Return evaluation response

        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception on error

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:  # Method to run full evaluation and return artifact
        """
        Method Name :   initiate_model_evaluation
        Description :   This function is used to initiate all steps of the model evaluation
        
        Output      :   Returns model evaluation artifact
        On Failure  :   Write an exception log and then raise an exception
        """  
        try:
            evaluate_model_response = self.evaluate_model()  # Get evaluation results
            s3_model_path = self.model_eval_config.s3_model_key_path  # Get S3 model path

            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=evaluate_model_response.is_model_accepted,  # Whether trained model is accepted
                s3_model_path=s3_model_path,  # S3 path of best model
                trained_model_path=self.model_trainer_artifact.trained_model_file_path,  # Path of trained model
                changed_accuracy=evaluate_model_response.difference)  # Accuracy difference

            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")  # Log artifact info
            return model_evaluation_artifact  # Return final artifact
        except Exception as e:
            raise USvisaException(e, sys) from e  # Raise custom exception on failure