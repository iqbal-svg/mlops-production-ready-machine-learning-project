import logging   # Python's built-in module for logging messages (info, errors, etc.)
import os        # Provides functions for interacting with the operating system

from from_root import from_root   # from_root() returns the project root folder path
from datetime import datetime     # Used to get the current date and time

# Create a log file name based on the current date and time
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Name of the folder where logs will be stored
log_dir = 'logs'

# Full path for the log file: project_root/logs/<log_file_name>
logs_path = os.path.join(from_root(), log_dir, LOG_FILE)

# Create the 'logs' directory if it doesn't already exist
os.makedirs(log_dir, exist_ok=True)

# Configure the logging system
logging.basicConfig(
    filename=logs_path,  # Save logs to the specified file path
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",  # Log message format
    level=logging.DEBUG,  # Minimum level of logs to capture (DEBUG and above)
)