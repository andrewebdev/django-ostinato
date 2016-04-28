FROM python:2.7

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    build-essential \
    python-dev \
    git \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libpq-dev \
    libjpeg-dev

ENV PYTHONBUFFERRED 1
RUN pip install --upgrade pip

RUN mkdir /demo

WORKDIR /demo/
ADD demo/requirements.txt /demo/requirements.txt
RUN pip install -r requirements.txt

