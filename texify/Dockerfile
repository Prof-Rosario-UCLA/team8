FROM python:3.13-slim-bookworm

RUN useradd -ms /bin/bash app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra

COPY requirements.txt /app/

RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

USER app

# TODO(bliutech): look into whether we can take advantage of Docker layer caching here
COPY . /app/


EXPOSE 9090

ENTRYPOINT [ "/app/start.sh" ]
