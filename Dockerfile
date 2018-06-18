FROM python:3.6-alpine

RUN adduser -D daniel

WORKDIR /home/website

COPY server_requirements.txt server_requirements.txt
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r server_requirements.txt


COPY blog blog
COPY blog.py blog/config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP blog.py

RUN chown -R daniel:daniel ./
USER daniel

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]