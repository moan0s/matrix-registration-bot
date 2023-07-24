FROM python:3-slim AS compile-image
MAINTAINER Julian-Samuel Gebühr

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install --no-cache-dir matrix-registration-bot

FROM python:3-slim

RUN apt-get update && libolm-dev
COPY --from=compile-image /opt/venv /opt/venv

VOLUME ["/data"]
WORKDIR /data

CMD ["/opt/venv/bin/matrix-registration-bot"]
