from fastapi import FastAPI, Request  # Import FastAPI framework and Request object
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware to handle cross-origin requests
from fastapi.responses import Response  # Import Response class for HTTP responses
from fastapi.staticfiles import StaticFiles  # Import StaticFiles to serve CSS, JS, images, etc.
from fastapi.templating import Jinja2Templates  # Import Jinja2 template engine for HTML rendering
from starlette.responses import HTMLResponse, RedirectResponse  # Extra response classes for HTML and redirects
from uvicorn import run as app_run  # Import uvicorn runner to run FastAPI app

from typing import Optional  # Import Optional for type hinting (nullable fields)

from us_visa.constants import APP_HOST, APP_PORT  # Import host and port settings from project constants
from us_visa.pipline.prediction_pipeline import USvisaData, USvisaClassifier  # Import data & model predictor classes
from us_visa.pipline.training_pipeline import TrainPipeline  # Import training pipeline class

app = FastAPI()  # Create FastAPI application instance

app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files from 'static' folder

templates = Jinja2Templates(directory='templates')  # Setup Jinja2 templates (HTML files in 'templates' folder)

origins = ["*"]  # Allow all origins for CORS (not secure for production, but works for dev)

app.add_middleware(   # Add CORS middleware to app
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from all domains
    allow_credentials=True,  # Allow cookies/credentials
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Class to handle form data coming from frontend
class DataForm:
    def __init__(self, request: Request):  # Constructor takes FastAPI Request object
        self.request: Request = request  # Store request
        # Define all possible form fields (initialize as None)
        self.continent: Optional[str] = None
        self.education_of_employee: Optional[str] = None
        self.has_job_experience: Optional[str] = None
        self.requires_job_training: Optional[str] = None
        self.no_of_employees: Optional[str] = None
        self.company_age: Optional[str] = None
        self.region_of_employment: Optional[str] = None
        self.prevailing_wage: Optional[str] = None
        self.unit_of_wage: Optional[str] = None
        self.full_time_position: Optional[str] = None
        

    async def get_usvisa_data(self):  # Method to extract data from HTML form
        form = await self.request.form()  # Await form submission data
        # Assign form values to class attributes
        self.continent = form.get("continent")
        self.education_of_employee = form.get("education_of_employee")
        self.has_job_experience = form.get("has_job_experience")
        self.requires_job_training = form.get("requires_job_training")
        self.no_of_employees = form.get("no_of_employees")
        self.company_age = form.get("company_age")
        self.region_of_employment = form.get("region_of_employment")
        self.prevailing_wage = form.get("prevailing_wage")
        self.unit_of_wage = form.get("unit_of_wage")
        self.full_time_position = form.get("full_time_position")

# Root endpoint (homepage)
@app.get("/", tags=["authentication"])  # GET request at root URL
async def index(request: Request):
    return templates.TemplateResponse(  # Render 'usvisa.html' with template engine
            "usvisa.html",{"request": request, "context": "Rendering"})

# Training endpoint
@app.get("/train")  # GET request at /train
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()  # Create training pipeline object
        train_pipeline.run_pipeline()  # Run the ML training pipeline
        return Response("Training successful !!")  # Success response
    except Exception as e:
        return Response(f"Error Occurred! {e}")  # Return error if training fails

# Prediction endpoint
@app.post("/")  # POST request at root URL
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)  # Create DataForm object with request
        await form.get_usvisa_data()  # Extract form data
        
        # Convert form data into USvisaData object
        usvisa_data = USvisaData(
                                continent= form.continent,
                                education_of_employee = form.education_of_employee,
                                has_job_experience = form.has_job_experience,
                                requires_job_training = form.requires_job_training,
                                no_of_employees= form.no_of_employees,
                                company_age= form.company_age,
                                region_of_employment = form.region_of_employment,
                                prevailing_wage= form.prevailing_wage,
                                unit_of_wage= form.unit_of_wage,
                                full_time_position= form.full_time_position,
                                )
        
        usvisa_df = usvisa_data.get_usvisa_input_data_frame()  # Convert input to DataFrame for ML model

        model_predictor = USvisaClassifier()  # Load trained classifier

        value = model_predictor.predict(dataframe=usvisa_df)[0]  # Predict visa approval (0 or 1)

        status = None
        if value == 1:  # If prediction is 1 → Approved
            status = "Visa-approved"
        else:  # If prediction is 0 → Not approved
            status = "Visa Not-Approved"

        return templates.TemplateResponse(  # Render result back to HTML page
            "usvisa.html",
            {"request": request, "context": status},
        )
        
    except Exception as e:
        return {"status": False, "error": f"{e}"}  # Return JSON error if prediction fails

# Run FastAPI app
if __name__ == "__main__":  # Run only if script is executed directly
    app_run(app, host=APP_HOST, port=APP_PORT)  # Start server with given host & port