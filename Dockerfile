FROM python:3.12-slim
WORKDIR /app
COPY . /app/
RUN apt-get update -y && apt-get install build-essential \
    libpq-dev -y && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt
RUN chmod +x ./start_local_api.sh
CMD [ "sh", "/app/start_local_api.sh" ]
