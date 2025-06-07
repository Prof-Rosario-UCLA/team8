# texify
Asynchronous job queue microservice for compiling LaTeX files to PDFs.

## Setting Up the Service
Set up a virtual environment and instally the dependencies.

```
cd texify/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Service
First, start by starting the Celery worker.

```
celery -A manager worker --loglevel=info
```

Next, start the server.

```
python app.py
```
