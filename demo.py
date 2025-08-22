from us_visa.pipline.training_pipeline import TrainPipeline  # Import the TrainPipeline class from the 'training_pipeline' module in the 'us_visa/pipline' package. This class is designed to manage the complete ML training process.
obj = TrainPipeline()  # Create an instance of the TrainPipeline class so we can call its methods.

obj.run_pipeline()  # Call the 'run_pipeline' method to start the end-to-end ML pipeline (data loading, preprocessing, model training, evaluation, saving results, etc.).
# from us_visa.logger import logging  # Import the logging module for logging messages in the US visa project.
# from us_visa.exception import USvisaException  # Import the custom exception class for handling errors in the US visa project.
# import sys
# #logging.info("welcome to our custom log")
# try:
#     a=2/0  # This line will raise a ZeroDivisionError because we are trying to divide by zero.
# except Exception as e:
#     raise USvisaException(e, sys)  # Catch the exception and raise a custom USvisaException with the error details.