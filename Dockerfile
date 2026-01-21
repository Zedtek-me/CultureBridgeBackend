FROM python
WORKDIR /app
COPY . /app/
RUN apt-get update -y && \
    pip install -r requirements.txt
RUN chmod +x ./start_local_api.sh
CMD [ "sh", "/app/start_local_api.sh" ]
