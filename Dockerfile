FROM python:3.6.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY project/requirements.txt /code/
RUN pip install -r requirements.txt
COPY project /code/