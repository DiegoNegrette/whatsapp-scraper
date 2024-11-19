FROM python:3.10.4

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_PORT 8000

VOLUME ["/code"]

COPY ./Pipfile ./
COPY ./Pipfile.lock ./

RUN python -m pip install --upgrade pip && \
  pip install pipenv && \
  pipenv install --system --dev && \
  rm -f Pipfile Pipfile.lock

# Add a text editor
RUN apt-get update && apt-get install -y nano dumb-init

# Install tzdata
RUN apt-get update && apt-get install -y tzdata

# Set timezone (optional, you can also handle this at runtime)
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Adds our application code to the image
COPY . /code
WORKDIR /code/whatsapp-scraper

EXPOSE ${DJANGO_PORT}