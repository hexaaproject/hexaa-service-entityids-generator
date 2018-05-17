FROM python:2-alpine
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY hexaa-service-entityids-generator.py ./

ENTRYPOINT [ "python", "./hexaa-service-entityids-generator.py" ]
