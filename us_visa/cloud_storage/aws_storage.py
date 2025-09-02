import boto3  # AWS SDK for Python, used to interact with AWS services like S3
from us_visa.configuration.aws_connection import S3Client  # Custom class to create an authenticated S3 client/resource
from io import StringIO  # In-memory text stream, useful for treating strings like file objects
from typing import Union, List  # Type hints for method inputs and outputs
import os, sys  # Standard Python libraries for OS operations and system-level exceptions
from us_visa.logger import logging  # Custom logging module for recording logs
from mypy_boto3_s3.service_resource import Bucket  # Type hint for an S3 Bucket object
from us_visa.exception import USvisaException  # Custom exception class for handling errors
from botocore.exceptions import ClientError  # AWS-specific exception for client errors
from pandas import DataFrame, read_csv  # Pandas for working with dataframes and reading CSVs
import pickle  # Python module for serializing and deserializing objects (used for ML models)


class SimpleStorageService:
    """
    A service class to interact with AWS S3 storage.

    It wraps boto3 functionality into simpler reusable methods
    for tasks like uploading files, reading objects, creating folders,
    checking keys, and loading ML models stored in S3.
    """

    def __init__(self):
        s3_client = S3Client()  # Initialize custom S3 client that reads AWS creds from env variables
        self.s3_resource = s3_client.s3_resource  # Boto3 high-level resource object for S3
        self.s3_client = s3_client.s3_client  # Boto3 low-level client object for S3

    def s3_key_path_available(self, bucket_name, s3_key) -> bool:
        try:
            bucket = self.get_bucket(bucket_name)  # Get the bucket object
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=s3_key)]  
            # Check if objects exist under the given S3 key (prefix)

            if len(file_objects) > 0:  # If at least one file exists
                return True
            else:
                return False
        except Exception as e:
            raise USvisaException(e, sys)  # Wrap error in custom exception class

    @staticmethod
    def read_object(object_name: str, decode: bool = True, make_readable: bool = False) -> Union[StringIO, str]:
        """
        Method Name :   read_object
        Description :   This method reads the object_name object with kwargs

        Output      :   The column name is renamed
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the read_object method of S3Operations class")

        try:
            func = (
                lambda: object_name.get()["Body"].read().decode()
                if decode is True
                else object_name.get()["Body"].read()
            )  # Reads S3 object body and decodes it into string if required
            conv_func = lambda: StringIO(func()) if make_readable is True else func()  
            # Optionally wrap in StringIO to behave like a file

            logging.info("Exited the read_object method of S3Operations class")
            return conv_func()  # Return either string, bytes, or file-like object

        except Exception as e:
            raise USvisaException(e, sys) from e  # Wrap exception

    def get_bucket(self, bucket_name: str) -> Bucket:
        """
        Method Name :   get_bucket
        Description :   This method gets the bucket object based on the bucket_name

        Output      :   Bucket object is returned based on the bucket name
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the get_bucket method of S3Operations class")

        try:
            bucket = self.s3_resource.Bucket(bucket_name)  # Get a bucket resource object
            logging.info("Exited the get_bucket method of S3Operations class")
            return bucket
        except Exception as e:
            raise USvisaException(e, sys) from e

    def get_file_object(self, filename: str, bucket_name: str) -> Union[List[object], object]:
        """
        Method Name :   get_file_object
        Description :   This method gets the file object from bucket_name bucket based on filename

        Output      :   list of objects or object is returned based on filename
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the get_file_object method of S3Operations class")

        try:
            bucket = self.get_bucket(bucket_name)  # Get the S3 bucket
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=filename)]  
            # Find objects matching filename prefix

            func = lambda x: x[0] if len(x) == 1 else x  # If only one object, return it instead of a list

            file_objs = func(file_objects)  # Apply logic
            logging.info("Exited the get_file_object method of S3Operations class")
            return file_objs
        except Exception as e:
            raise USvisaException(e, sys) from e

    def load_model(self, model_name: str, bucket_name: str, model_dir: str = None) -> object:
        """
        Method Name :   load_model
        Description :   This method loads the model_name model from bucket_name bucket with kwargs

        Output      :   list of objects or object is returned based on filename
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the load_model method of S3Operations class")

        try:
            func = (
                lambda: model_name if model_dir is None else model_dir + "/" + model_name
            )  # Build S3 path for model
            model_file = func()
            file_object = self.get_file_object(model_file, bucket_name)  # Fetch model file from S3
            model_obj = self.read_object(file_object, decode=False)  # Read as bytes (no decode)
            model = pickle.loads(model_obj)  # Deserialize object back into Python model
            logging.info("Exited the load_model method of S3Operations class")
            return model
        except Exception as e:
            raise USvisaException(e, sys) from e

    def create_folder(self, folder_name: str, bucket_name: str) -> None:
        """
        Method Name :   create_folder
        Description :   This method creates a folder_name folder in bucket_name bucket

        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the create_folder method of S3Operations class")

        try:
            self.s3_resource.Object(bucket_name, folder_name).load()  
            # Check if folder already exists
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":  # If not found
                folder_obj = folder_name + "/"  # Add trailing slash for folder in S3
                self.s3_client.put_object(Bucket=bucket_name, Key=folder_obj)  # Create empty folder
            else:
                pass  # Ignore other errors
            logging.info("Exited the create_folder method of S3Operations class")

    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True):
        """
        Method Name :   upload_file
        Description :   This method uploads the from_filename file to bucket_name bucket with to_filename as bucket filename

        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the upload_file method of S3Operations class")

        try:
            logging.info(f"Uploading {from_filename} file to {to_filename} file in {bucket_name} bucket")

            self.s3_resource.meta.client.upload_file(from_filename, bucket_name, to_filename)  
            # Upload local file to S3

            logging.info(f"Uploaded {from_filename} file to {to_filename} file in {bucket_name} bucket")

            if remove is True:  # If remove flag is set
                os.remove(from_filename)  # Delete local file
                logging.info(f"Remove is set to {remove}, deleted the file")
            else:
                logging.info(f"Remove is set to {remove}, not deleted the file")

            logging.info("Exited the upload_file method of S3Operations class")
        except Exception as e:
            raise USvisaException(e, sys) from e

    def upload_df_as_csv(self, data_frame: DataFrame, local_filename: str, bucket_filename: str, bucket_name: str) -> None:
        """
        Method Name :   upload_df_as_csv
        Description :   This method uploads the dataframe to bucket_filename csv file in bucket_name bucket

        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the upload_df_as_csv method of S3Operations class")

        try:
            data_frame.to_csv(local_filename, index=None, header=True)  # Save DataFrame to CSV locally
            self.upload_file(local_filename, bucket_filename, bucket_name)  # Upload to S3
            logging.info("Exited the upload_df_as_csv method of S3Operations class")
        except Exception as e:
            raise USvisaException(e, sys) from e

    def get_df_from_object(self, object_: object) -> DataFrame:
        """
        Method Name :   get_df_from_object
        Description :   This method gets the dataframe from the object_name object

        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the get_df_from_object method of S3Operations class")

        try:
            content = self.read_object(object_, make_readable=True)  # Read file into StringIO
            df = read_csv(content, na_values="na")  # Parse CSV into pandas DataFrame
            logging.info("Exited the get_df_from_object method of S3Operations class")
            return df
        except Exception as e:
            raise USvisaException(e, sys) from e

    def read_csv(self, filename: str, bucket_name: str) -> DataFrame:
        """
        Method Name :   get_df_from_object
        Description :   This method gets the dataframe from the object_name object

        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        logging.info("Entered the read_csv method of S3Operations class")

        try:
            csv_obj = self.get_file_object(filename, bucket_name)  # Get CSV object from S3
            df = self.get_df_from_object(csv_obj)  # Convert object into DataFrame
            logging.info("Exited the read_csv method of S3Operations class")
            return df
        except Exception as e:
            raise USvisaException(e, sys) from e
# 📄 One-page explanation:

# Purpose: SimpleStorageService wraps around boto3 to make S3 operations easier in your project.

# Initialization (__init__) → creates an S3 client and resource using environment variables.

# Check if file/folder exists (s3_key_path_available) → verifies if a given key/prefix exists in a bucket.

# Read object (read_object) → downloads and optionally decodes S3 object, returns as string, bytes, or file-like object.

# Get bucket (get_bucket) → returns an S3 Bucket object by name.

# Get file (get_file_object) → finds one or more files in a bucket by prefix.

# Load model (load_model) → loads a serialized ML model (pickled object) from S3.

# Create folder (create_folder) → makes a folder in S3 (really just an empty object ending in “/”).

# Upload file (upload_file) → uploads local file to S3, can optionally remove local copy.

# Upload DataFrame (upload_df_as_csv) → saves a Pandas DataFrame to CSV and uploads it.

# Get DataFrame (get_df_from_object) → reads an S3 CSV file object into a Pandas DataFrame.

# Read CSV (read_csv) → gets CSV file directly from S3 bucket into Pandas.

# So basically, this class is your S3 utility toolkit — instead of writing raw boto3 code everywhere, you centralize it here with logging and custom error handling.