FROM python:3.13-slim-bookworm

WORKDIR /app

RUN python3 -m pip install --no-cache-dir flask gunicorn Flask-Cors

COPY . /app/

EXPOSE 9000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:9000", "app:app"]
