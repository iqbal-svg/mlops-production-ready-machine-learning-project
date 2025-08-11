import os  # Import the os module for interacting with the operating system (not used in this snippet but maybe used elsewhere)
import sys  # Import the sys module for accessing system-specific parameters and functions

def error_message_detail(error, error_detail: sys):
    # Function to extract detailed error info from an exception
    _, _, exc_tb = error_detail.exc_info()  # Get the traceback object from the exception info
    file_name = exc_tb.tb_frame.f_code.co_filename  # Get the file name where the exception occurred
    error_message = "Error occurred python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name, exc_tb.tb_lineno, str(error)  # Format the error details into a readable string
    )
    return error_message  # Return the formatted error message

class USvisaException(Exception):
    # Custom exception class for US visa project errors
    def __init__(self, error_message, error_detail):
        """
        :param error_message: error message in string format
        """
        super().__init__(error_message)  # Initialize base Exception class with the provided message
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail  # Generate the detailed error message
        )

    def __str__(self):
        return self.error_message  # When printed, this exception shows the detailed error message