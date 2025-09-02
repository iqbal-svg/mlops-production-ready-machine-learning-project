from us_visa.cloud_storage.aws_storage import SimpleStorageService  # Importing a helper class to interact with AWS S3
from us_visa.exception import USvisaException  # Custom exception class for handling errors in the project
from us_visa.entity.estimator import USvisaModel  # Importing the model entity class (used for prediction)
import sys  # Provides access to system-specific parameters and functions (e.g., error handling)
from pandas import DataFrame  # Importing DataFrame class from pandas for handling tabular data


class USvisaEstimator:
    """
    This class is used to save and retrieve us_visas model in s3 bucket and to do prediction
    """

    def __init__(self,bucket_name,model_path,):
        """
        :param bucket_name: Name of your model bucket
        :param model_path: Location of your model in bucket
        """
        self.bucket_name = bucket_name  # Store the bucket name where the model will be saved/loaded
        self.s3 = SimpleStorageService()  # Create an object to interact with AWS S3
        self.model_path = model_path  # Path to the model file inside the S3 bucket
        self.loaded_model:USvisaModel=None  # Initialize a placeholder for the model once it is loaded


    def is_model_present(self,model_path):
        try:
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name, s3_key=model_path)  
            # Check if a model file exists at the given path in the S3 bucket
        except USvisaException as e:
            print(e)  # Print the exception if something goes wrong
            return False  # Return False if the model is not found or error occurs


    def load_model(self,)->USvisaModel:
        """
        Load the model from the model_path
        :return:
        """
        return self.s3.load_model(self.model_path,bucket_name=self.bucket_name)  
        # Load and return the model stored at model_path in the given S3 bucket


    def save_model(self,from_file,remove:bool=False)->None:
        """
        Save the model to the model_path
        :param from_file: Your local system model path
        :param remove: By default it is false that mean you will have your model locally available in your system folder
        :return:
        """
        try:
            self.s3.upload_file(from_file,  
                                to_filename=self.model_path,  
                                bucket_name=self.bucket_name,  
                                remove=remove  
                                )  
            # Upload the model file from the local system to the S3 bucket.
            # If remove=True, delete the local file after upload.
        except Exception as e:
            raise USvisaException(e, sys)  # Wrap and raise the exception as a custom USvisaException


    def predict(self,dataframe:DataFrame):
        """
        :param dataframe:
        :return:
        """
        try:
            if self.loaded_model is None:  # Check if the model has already been loaded
                self.loaded_model = self.load_model()  # If not, load it from S3
            return self.loaded_model.predict(dataframe=dataframe)  
            # Perform prediction using the loaded model on the given DataFrame
        except Exception as e:
            raise USvisaException(e, sys)  # Raise custom exception if prediction fails