FROM python:3.8-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV TZ Asia/Tehran

# set work directory
RUN mkdir /code
WORKDIR /code

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile /code/
COPY Pipfile.lock /code/

RUN pipenv install --system --deploy

COPY . .
