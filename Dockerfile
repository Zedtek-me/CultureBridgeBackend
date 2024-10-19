FROM python:3
WORKDIR /app
RUN apt-get update -y
COPY . /app/
RUN pip install -r requirements.txt
COPY start_api.sh /app/start_api.sh
RUN chmod +x start_api.sh
ENTRYPOINT [ "sh", "-c", "/app/start_api.sh" ]
