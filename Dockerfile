FROM python:3-alpine
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY hexaa-service-entityids-generator.py ./

ENTRYPOINT [ "python3", "./hexaa-service-entityids-generator.py" ]
