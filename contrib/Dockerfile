FROM python:latest
MAINTAINER Julian-Samuel Gebühr

RUN apt-get update && apt-get install -y pip
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -i https://test.pypi.org/simple/ matrix-registration-bot
VOLUME ["/data"]
CMD ["matrix-registration-bot"]

