FROM python:3.7

COPY ./requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt

# TODO: Remove the reload. It's just there for dev purposes
CMD uvicorn app:app --host 0.0.0.0 --reload

