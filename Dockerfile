FROM python:3-alpine
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY hexaa-service-entityids-generator.py ./

RUN adduser -S www-data -u 1033

USER www-data

ENTRYPOINT [ "python3", "./hexaa-service-entityids-generator.py" ]
