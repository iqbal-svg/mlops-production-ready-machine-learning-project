from us_visa.cloud_storage.aws_storage import SimpleStorageService  # Import custom class to interact with AWS S3 storage
from us_visa.exception import USvisaException  # Custom exception class for handling errors in the project
from us_visa.logger import logging  # Custom logging utility for tracking execution flow and errors
from us_visa.entity.artifact_entity import ModelPusherArtifact, ModelEvaluationArtifact  # Entity classes to represent artifacts for model pushing and evaluation
from us_visa.entity.config_entity import ModelPusherConfig  # Configuration entity for model pusher (bucket name, model path, etc.)
from us_visa.entity.s3_estimator import USvisaEstimator  # Custom estimator class that handles saving/loading model to/from S3
import sys

class ModelPusher:  # Defines a class responsible for pushing (uploading) trained models to S3
    def __init__(self, model_evaluation_artifact: ModelEvaluationArtifact,
                 model_pusher_config: ModelPusherConfig):  # Constructor takes evaluation artifact and pusher config
        """
        :param model_evaluation_artifact: Output reference of data evaluation artifact stage
        :param model_pusher_config: Configuration for model pusher
        """
        self.s3 = SimpleStorageService()  # Create an instance to interact with AWS S3
        self.model_evaluation_artifact = model_evaluation_artifact  # Store the model evaluation artifact (contains trained model path, etc.)
        self.model_pusher_config = model_pusher_config  # Store the pusher configuration (contains bucket name, key paths, etc.)
        self.usvisa_estimator = USvisaEstimator(bucket_name=model_pusher_config.bucket_name,
                                model_path=model_pusher_config.s3_model_key_path)  # Create estimator object to handle saving/loading model in S3

    def initiate_model_pusher(self) -> ModelPusherArtifact:  # Method to perform the model pushing process and return an artifact
        """
        Method Name :   initiate_model_evaluation
        Description :   This function is used to initiate all steps of the model pusher
        
        Output      :   Returns model evaluation artifact
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info("Entered initiate_model_pusher method of ModelTrainer class")  # Log entry into method

        try:
            logging.info("Uploading artifacts folder to s3 bucket")  # Log start of upload

            # Save/upload the trained model file to S3 using the estimator
            self.usvisa_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)

            # Create a ModelPusherArtifact instance with S3 bucket details for tracking
            model_pusher_artifact = ModelPusherArtifact(bucket_name=self.model_pusher_config.bucket_name,
                                                        s3_model_path=self.model_pusher_config.s3_model_key_path)

            logging.info("Uploaded artifacts folder to s3 bucket")  # Log success of upload
            logging.info(f"Model pusher artifact: [{model_pusher_artifact}]")  # Log details of the artifact
            logging.info("Exited initiate_model_pusher method of ModelTrainer class")  # Log exit from method
            
            return model_pusher_artifact  # Return artifact object containing bucket and model path info
        except Exception as e:  # Catch exceptions if anything fails
            raise USvisaException(e, sys) from e  # Raise custom exception with original traceback for debugging