FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/

RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# TODO(bliutech): look into whether we can take advantage of Docker layer caching here
COPY . /app/

EXPOSE 5001

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5001", "app:app"]
