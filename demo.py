from us_visa.pipline.training_pipeline import TrainPipeline  # Import the TrainPipeline class from the 'training_pipeline' module in the 'us_visa/pipline' package. This class is designed to manage the complete ML training process.

obj = TrainPipeline()  # Create an instance of the TrainPipeline class so we can call its methods.

obj.run_pipeline()  # Call the 'run_pipeline' method to start the end-to-end ML pipeline (data loading, preprocessing, model training, evaluation, saving results, etc.).