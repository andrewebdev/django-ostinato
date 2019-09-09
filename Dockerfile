FROM python:3
ENV PYTHONBUFFERRED 1
RUN pip install --upgrade pip

RUN mkdir /src
ADD . /src/

WORKDIR /src/demo/
RUN pip install -r requirements.txt
