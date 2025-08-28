import os
from datetime import date

DATABASE_NAME = "us_visa"
COLLECTION_NAME = "visa_data"
MONGODB_URL_KEY = "MONGODB_URL"

PIPELINE_NAME: str = "usvisa"
ARTIFACT_DIR: str = "artifact"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

FILE_NAME: str = "usvisa.csv"
MODEL_FILE_NAME = "model.pkl"

TARGET_COLUMN = "case_status"
CURRENT_YEAR = date.today().year
PREPROCSSING_OBJECT_FILE_NAME = "preprocessing.pkl"
SCHEMA_FILE_PATH = os.path.join("config", "schema.yaml")

#Data Ingestion related constant start with DATA_INGESTION VAR NAME
# MongoDB collection name where raw data is stored
DATA_INGESTION_COLLECTION_NAME: str = "visa_data"  

# Main directory for data ingestion artifacts
DATA_INGESTION_DIR_NAME: str = "data_ingestion"  

# Sub-directory to store raw data (feature store = permanent storage of original features)
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"  

# Sub-directory to store train/test split data after ingestion
DATA_INGESTION_INGESTED_DIR: str = "ingested"  

# Ratio for splitting data into test set (e.g., 0.2 means 20% test, 80% train)
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2

"""
Data Validation realted contant start with DATA_VALIDATION VAR NAME
"""
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"

"""
Data Transformation ralated constant start with DATA_TRANSFORMATION VAR NAME
"""
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR: str = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str = "transformed_object"