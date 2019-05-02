FROM python:3-alpine
WORKDIR /usr/src/app

COPY requirements.txt ./

COPY hexaa-service-entityids-generator.py ./

RUN pip install --no-cache-dir -r requirements.txt \
    && addgroup -S www-data \
    && adduser -S -G www-data www-data

USER www-data

ENTRYPOINT [ "python3", "./hexaa-service-entityids-generator.py" ]
