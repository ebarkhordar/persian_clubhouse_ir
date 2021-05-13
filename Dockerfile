FROM python:3.8-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV TZ Asia/Tehran

# set work directory
RUN mkdir /code
WORKDIR /code

RUN apt update -y
RUN apt install -y libpq-dev python-dev gcc

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile /code/
COPY Pipfile.lock /code/

RUN pipenv install --system --deploy

COPY . .

CMD ["python", "manage.py", "migrate"]
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "persian_clubhouse_ir.wsgi:application"]
CMD ["python", "manage.py", "start_bot"]