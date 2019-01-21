FROM python:3
ENV PYTHONBUFFERRED 1
RUN pip install --upgrade pip

RUN mkdir /src

WORKDIR /src/
ADD . /src/

WORKDIR /src/
RUN pip install -r demo/requirements.txt

WORKDIR /src/demo/
RUN python manage.py migrate
