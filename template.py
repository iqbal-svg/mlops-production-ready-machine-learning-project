import os  # Used for creating directories and checking file existence
from pathlib import Path  # Helps handle file paths in an OS-independent way

project_name = "us_visa"  # Define the main project folder name

# List of files and folders to be created
list_of_files = [
    f"{project_name}/__init__.py",  # Makes 'us_visa' a Python package
    f"{project_name}/components/__init__.py",  # Makes 'components' a Python subpackage
    f"{project_name}/components/data_ingestion.py",  # Placeholder for data ingestion logic
    f"{project_name}/components/data_validation.py",  # Placeholder for data validation logic
    f"{project_name}/components/data_transformation.py",  # Placeholder for data transformation logic
    f"{project_name}/components/model_trainer.py",  # Placeholder for model training code
    f"{project_name}/components/model_evaluation.py",  # Placeholder for model evaluation code
    f"{project_name}/components/model_pusher.py",  # Placeholder for model deployment logic
    f"{project_name}/configuration/__init__.py",  # For config-related code
    f"{project_name}/constants/__init__.py",  # For defining constants
    f"{project_name}/entity/__init__.py",  # For defining input/output schema entities
    f"{project_name}/entity/config_entity.py",  # Configuration entity definitions
    f"{project_name}/entity/artifact_entity.py",  # Artifact entity definitions
    f"{project_name}/exception/__init__.py",  # Custom exception handling module
    f"{project_name}/logger/__init__.py",  # Logging module
    f"{project_name}/pipline/__init__.py",  # Typo: should be 'pipeline' (used for pipeline logic)
    f"{project_name}/pipline/training_pipeline.py",  # Typo: should be 'pipeline' (training pipeline script)
    f"{project_name}/pipline/prediction_pipeline.py",  # Typo: should be 'pipeline' (prediction pipeline script)
    f"{project_name}/utils/__init__.py",  # Utility functions module
    f"{project_name}/utils/main_utils.py",  # Main helper functions
    "app.py",  # Main entry-point for running app or API
    "requirements.txt",  # Lists Python packages required for the project
    "Dockerfile",  # Used to containerize the project using Docker
    ".dockerignore",  # Specifies files/folders to ignore in Docker build context
    "demo.py",  # For demo or testing code
    "setup.py",  # Package metadata and installation script
    "config/model.yaml",  # YAML file for model configuration
    "config/schema.yaml",  # YAML file for data schema
]

# Iterate over each file path in the list
for filepath in list_of_files:
    filepath = Path(filepath)  # Convert string path to a Path object for flexibility
    filedir, filename = os.path.split(filepath)  # Split the path into folder (filedir) and file name

    if filedir != "":  # If there's a directory path (not just a file in current dir)
        os.makedirs(filedir, exist_ok=True)  # Create the directory if it doesn’t exist

    # Create the file if it doesn't exist or it's an empty file
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:  # Open the file in write mode
            pass  # Create an empty file (do nothing else)
    else:
        print(f"file is already present at: {filepath}")  # If the file exists and isn't empty, print a messageS