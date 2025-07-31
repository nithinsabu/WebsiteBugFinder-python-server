This project is the FastAPI server to interact with gemini to analyse a given html with optional specifications and a design file.
Python version used: 3.13
To run this project, 2 environment variables are necessary: 
    GEMINI_API_KEY= <Provide your gemini API KEY>
    MODEL=<Provide the gemini model> eg. gemini-2.5-flash
If using an .env file, make sure to place it at the root of the project (same level as /app).

Steps to run locally:
1. Create a virtual environment: python -m venv venv
2. Activate the virtual environment: venv/Scripts/activate
3. Install the libraries used: pip install -r requirements.txt
4. Run the app: fastapi dev app/main.py
(Runs on port 8000)

To run the docker image:
1. docker build -t fastapi-app .
2. docker run -e GEMINI_API_KEY=<Provide your gemini API KEY> -e MODEL=<Provide your gemini model> --network <Provide docker network name> --name <Provide alias> fastapi-app
(Runs on port 80 of the container)

Example run:
docker run -e GEMINI_API_KEY=xxxxxxxx -e MODEL=gemini-2.5-flash --name fastapi-app --network wbfapp fastapi-app