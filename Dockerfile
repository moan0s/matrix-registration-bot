FROM python:3.11-slim AS compile-image
MAINTAINER Julian-Samuel Gebühr


RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libolm-dev

RUN python -m venv /opt/venv

WORKDIR /app
COPY requirements.txt ./
RUN /opt/venv/bin/pip install -r requirements.txt
COPY . .
RUN /opt/venv/bin/pip install .
RUN /opt/venv/bin/pip install matrix-nio==0.20.2

FROM python:3.11-slim

RUN apt-get update && apt-get install -y libolm-dev
COPY --from=compile-image /opt/venv /opt/venv

VOLUME ["/data"]
WORKDIR /data

CMD ["/opt/venv/bin/matrix-registration-bot"]
