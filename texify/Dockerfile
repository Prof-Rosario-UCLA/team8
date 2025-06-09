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

COPY --chown=app:app . /app/

EXPOSE 8080

ENTRYPOINT [ "/app/start.sh" ]
