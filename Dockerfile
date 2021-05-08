FROM python:3.9.5 as producer

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

ADD src /app/src

WORKDIR /app/src

CMD python3.9 producer_metrics.py

FROM producer as consumer

CMD python3.9 consumer_metrics.py
