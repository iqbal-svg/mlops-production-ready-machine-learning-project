import sys  # Provides system-specific parameters and functions (used here mainly for exception handling)
from us_visa.exception import USvisaException  # Custom exception class for handling project-specific errors
from us_visa.logger import logging  # Custom logging module for logging info, warnings, errors, etc.

# Importing pipeline components (each represents a stage in ML pipeline)
from us_visa.components.data_ingestion import DataIngestion  # Responsible for fetching and splitting data into train/test
from us_visa.components.data_validation import DataValidation  # Responsible for checking data quality and schema validation
from us_visa.components.data_transformation import DataTransformation  # Handles preprocessing, scaling, feature engineering
from us_visa.components.model_trainer import ModelTrainer  # Responsible for training ML/DL models
# from us_visa.components.model_evaluation import ModelEvaluation  # Responsible for evaluating model performance
# from us_visa.components.model_pusher import ModelPusher  # Responsible for pushing final model to deployment/storage

# Importing config entities (input configurations for each pipeline component)
from us_visa.entity.config_entity import (DataIngestionConfig,  # Config for ingestion
                                          DataValidationConfig,  # Config for validation
                                          DataTransformationConfig,  # Config for transformation
                                          ModelTrainerConfig)  # Config for trainer
                                        #   ModelEvaluationConfig,  # Config for evaluation
                                        #   ModelPusherConfig)  # Config for pushing

# Importing artifact entities (outputs of each pipeline component)
from us_visa.entity.artifact_entity import (DataIngestionArtifact, # Artifact produced after ingestion
                                            DataValidationArtifact,  # Artifact produced after validation
                                            DataTransformationArtifact,  # Artifact produced after transformation
                                            ModelTrainerArtifact)  # Artifact produced after training
                                            # ModelEvaluationArtifact,  # Artifact produced after evaluation
                                            # ModelPusherArtifact)  # Artifact produced after pushing

class TrainPipeline:  # Defines the entire ML training pipeline class
    def __init__(self):  # Constructor initializes all pipeline configuration objects
        self.data_ingestion_config = DataIngestionConfig()  # Load config for data ingestion
        self.data_validation_config = DataValidationConfig()  # Load config for data validation
        self.data_transformation_config = DataTransformationConfig()  # Load config for data transformation
        self.model_trainer_config = ModelTrainerConfig()  # Load config for model trainer
        # self.model_evaluation_config = ModelEvaluationConfig()  # Load config for model evaluation
        # self.model_pusher_config = ModelPusherConfig()  # Load config for model pushing

    def start_data_ingestion(self) -> DataIngestionArtifact:  # Method to run data ingestion step
        try:
            logging.info("Entered the start_data_ingestion method of TrainPipeline class")  # Log entry
            logging.info("Getting the data from mongodb")  # Log source of data
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)  # Create ingestion object with config
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()  # Run ingestion: fetch, split train/test, save
            logging.info("Got the train_set and test_set from mongodb")  # Log completion
            logging.info("Exited the start_data_ingestion method of TrainPipeline class")  # Log exit
            return data_ingestion_artifact  # Return ingestion artifact (paths to train/test CSVs)
        except Exception as e:  # If error occurs
            raise USvisaException(e, sys) from e  # Raise custom exception

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:  # Run validation step
        logging.info("Entered the start_data_validation method of TrainPipeline class")  # Log entry
        try:
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                             data_validation_config=self.data_validation_config)  # Create validation object with configs + ingestion data
            data_validation_artifact = data_validation.initiate_data_validation()  # Run validation (check schema, missing values, etc.)
            logging.info("Performed the data validation operation")  # Log validation done
            logging.info("Exited the start_data_validation method of TrainPipeline class")  # Log exit
            return data_validation_artifact  # Return validation results
        except Exception as e:  # If error occurs
            raise USvisaException(e, sys) from e  # Raise custom exception

    def start_data_transformation(self, data_ingestion_artifact: DataIngestionArtifact,
                                  data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:  # Run transformation step
        try:
            data_transformation = DataTransformation(data_ingestion_artifact=data_ingestion_artifact,
                                                     data_transformation_config=self.data_transformation_config,
                                                     data_validation_artifact=data_validation_artifact)  # Create transformation object
            data_transformation_artifact = data_transformation.initiate_data_transformation()  # Run preprocessing (scaling, encoding, etc.)
            return data_transformation_artifact  # Return transformation artifact
        except Exception as e:  # If error occurs
            raise USvisaException(e, sys)  # Raise custom exception

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:  # Run training step
        try:
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                                         model_trainer_config=self.model_trainer_config)  # Create trainer object
            model_trainer_artifact = model_trainer.initiate_model_trainer()  # Train ML/DL model
            return model_trainer_artifact  # Return trainer artifact (model path, metrics, etc.)
        except Exception as e:  # If error occurs
            raise USvisaException(e, sys)  # Raise custom exception

    # def start_model_evaluation(self, data_ingestion_artifact: DataIngestionArtifact,
    #                            model_trainer_artifact: ModelTrainerArtifact) -> ModelEvaluationArtifact:  # Run evaluation step
    #     try:
    #         model_evaluation = ModelEvaluation(model_eval_config=self.model_evaluation_config,
    #                                            data_ingestion_artifact=data_ingestion_artifact,
    #                                            model_trainer_artifact=model_trainer_artifact)  # Create evaluation object
    #         model_evaluation_artifact = model_evaluation.initiate_model_evaluation()  # Run evaluation (compare models, check metrics)
    #         return model_evaluation_artifact  # Return evaluation artifact
    #     except Exception as e:  # If error occurs
    #         raise USvisaException(e, sys)  # Raise custom exception

    # def start_model_pusher(self, model_evaluation_artifact: ModelEvaluationArtifact) -> ModelPusherArtifact:  # Run pushing step
    #     try:
    #         model_pusher = ModelPusher(model_evaluation_artifact=model_evaluation_artifact,
    #                                    model_pusher_config=self.model_pusher_config)  # Create pusher object
    #         model_pusher_artifact = model_pusher.initiate_model_pusher()  # Push model to deployment/registry
    #         return model_pusher_artifact  # Return pusher artifact (saved model path/location)
    #     except Exception as e:  # If error occurs
    #         raise USvisaException(e, sys)  # Raise custom exception

    def run_pipeline(self) -> None:  # Orchestrates the full training pipeline
        try:
            data_ingestion_artifact = self.start_data_ingestion()  # Step 1: Run ingestion
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)  # Step 2: Run validation
            data_transformation_artifact = self.start_data_transformation(
                 data_ingestion_artifact=data_ingestion_artifact,
                 data_validation_artifact=data_validation_artifact)  # Step 3: Run transformation
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)  # Step 4: Train model
        #     model_evaluation_artifact = self.start_model_evaluation(data_ingestion_artifact=data_ingestion_artifact,
        #                                                             model_trainer_artifact=model_trainer_artifact)  # Step 5: Evaluate model
        #     if not model_evaluation_artifact.is_model_accepted:  # Check if trained model is better than previous one
        #         logging.info(f"Model not accepted.")  # Log rejection
        #         return None  # Stop pipeline if model is not better
        #     model_pusher_artifact = self.start_model_pusher(model_evaluation_artifact=model_evaluation_artifact)  # Step 6: Push model if accepted
        except Exception as e:  # If error occurs
            raise USvisaException(e, sys)  # Raise custom exception
        
# write in demo.py to call method run_pipeline()
# from us_visa.pipline.training_pipeline import TrainPipeline

# obj = TrainPipeline()
# obj.run_pipeline()