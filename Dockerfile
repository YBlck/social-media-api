FROM python:3.11.11-alpine3.21
LABEL maintainer="chorny.yura@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /files/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    social_media_user

RUN chown -R social_media_user /files/media
RUN chmod -R 755 /files/media

USER social_media_user