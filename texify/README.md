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

Use an `.env` file that looks like the following.

```
GCS_BUCKET_NAME=test-bucket
GCS_EMULATOR_HOST=http://localhost:4443
GCS_EMULATOR=1
```

## Running the Service
First, start by starting the Fake GCS service.

```
docker-compose up
```

Next, start the Celery worker.

```
celery -A manager worker --loglevel=info
```

Next, start the server.

```
python app.py
```
