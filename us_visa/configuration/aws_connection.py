import boto3  # AWS SDK for Python, used to interact with AWS services like S3
import os  # Provides a way to access environment variables and interact with the operating system
from us_visa.constants import AWS_SECRET_ACCESS_KEY_ENV_KEY, AWS_ACCESS_KEY_ID_ENV_KEY, REGION_NAME  
# Import constants for AWS environment variable keys and default region name from your project

class S3Client:  # Defines a class to handle S3 connections

    s3_client = None  # Class variable to hold the S3 client instance (shared by all objects of this class)
    s3_resource = None  # Class variable to hold the S3 resource instance (shared by all objects of this class)

    def __init__(self, region_name=REGION_NAME):  
        # Constructor initializes S3 connection. By default, uses REGION_NAME from constants.

        """ 
        This Class gets aws credentials from env_variable and creates an connection with s3 bucket 
        and raise exception when environment variable is not set
        """
        # Docstring: explains that this class reads AWS credentials from environment variables
        # and establishes a connection to S3, raising an exception if variables are missing.

        if S3Client.s3_resource == None or S3Client.s3_client == None:  
            # If no connection has been created yet (first time using this class)

            __access_key_id = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY,)  
            # Get AWS Access Key ID from environment variables using the key name defined in constants

            __secret_access_key = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY,)  
            # Get AWS Secret Access Key from environment variables using the key name defined in constants

            if __access_key_id is None:  
                # If the access key is missing
                raise Exception(f"Environment variable: {AWS_ACCESS_KEY_ID_ENV_KEY} is not not set.")  
                # Raise an exception telling which environment variable is missing

            if __secret_access_key is None:  
                # If the secret key is missing
                raise Exception(f"Environment variable: {AWS_SECRET_ACCESS_KEY_ENV_KEY} is not set.")  
                # Raise an exception telling which environment variable is missing

            S3Client.s3_resource = boto3.resource('s3',  
                                            aws_access_key_id=__access_key_id,  
                                            aws_secret_access_key=__secret_access_key,  
                                            region_name=region_name  
                                            )  
            # Create an S3 *resource* (high-level object-oriented API for S3) and store it in class variable

            S3Client.s3_client = boto3.client('s3',  
                                        aws_access_key_id=__access_key_id,  
                                        aws_secret_access_key=__secret_access_key,  
                                        region_name=region_name  
                                        )  
            # Create an S3 *client* (low-level API for S3) and store it in class variable

        self.s3_resource = S3Client.s3_resource  
        # Set the instance's s3_resource attribute to the shared class-level resource

        self.s3_client = S3Client.s3_client  
        # Set the instance's s3_client attribute to the shared class-level client