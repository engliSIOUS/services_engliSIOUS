## How to Run This Project

1. **Clone the Repository**  
    Clone this repository to your local machine using the following command:  


2. **Navigate to the Project Directory**  
    Change your working directory to the project folder


3. **Install Dependencies And Local Environment**  
    Ensure you have Python installed. Then, install the environment and required dependencies using:  
    python -m venv venv
    venv\Scripts\activate     
    pip install -r requirements.txt


4. **Run the Application**  
    Start the application by executing the main script:  

    uvicorn main:app --reload   


5. **Access the Service**  
    Open your browser and navigate to the provided URL (e.g., `http://localhost:8000`) to interact with the service.
