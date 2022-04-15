FROM python:latest
MAINTAINER Julian-Samuel Gebühr

RUN apt-get update && apt-get install -y pip
RUN pip install matrix-registration-bot
CMD ["python3", "-m",  "matrix_registration_bot.bot"]