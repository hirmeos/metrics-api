FROM python:2

RUN apt-get update && apt-get -y install apt-utils supervisor

WORKDIR /usr/src/app

COPY ./config/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY ./config/supervisord.conf /etc/supervisor/supervisord.conf
COPY ./config/services.yaml /etc/supervisor/services.yaml

COPY ./src/* ./

RUN flake8 --ignore=E221,E241 ./

EXPOSE 8080

ENTRYPOINT  ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
