FROM python:3.10-alpine

RUN apk add git build-base python3 py3-pip 
RUN pip install pipenv

RUN mkdir -p /iebs2
COPY . /iebs2/
WORKDIR /iebs2
RUN pipenv install --system --deploy

ENTRYPOINT ["python", "server.py"]
