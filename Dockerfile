FROM python:latest
MAINTAINER Julian-Samuel Gebühr

RUN apt-get update && apt-get install -y pip
RUN pip install matrix-registration-bot
VOLUME ["/data"]
WORKDIR /data
CMD ["matrix-registration-bot"]
