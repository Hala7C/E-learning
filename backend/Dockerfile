FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
COPY .env  /django/.env

WORKDIR /django


COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# COPY . .

# CMD [ "python3","manage.py","runserver","0.0.0.0:8000" ]