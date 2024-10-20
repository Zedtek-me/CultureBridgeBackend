FROM python
WORKDIR /app
RUN apt-get update -y
COPY . /app/
RUN pip install -r requirements.txt
RUN chmod +x ./start_local_api.sh
ENTRYPOINT [ "sh", "/app/start_local_api.sh" ]
