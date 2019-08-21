FROM python:3.5

RUN apt-get update && apt-get -y install apt-utils supervisor

WORKDIR /usr/src/app

COPY ./config/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY ./config/supervisord.conf /etc/supervisor/supervisord.conf
COPY ./config/services.yaml /etc/supervisor/services.yaml

ADD ./src/ ./

RUN flake8 ./

EXPOSE 8080

ENTRYPOINT  ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
