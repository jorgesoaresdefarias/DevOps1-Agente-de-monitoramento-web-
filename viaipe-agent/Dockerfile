FROM python:3.10

RUN apt-get update && apt-get install -y iputils-ping

WORKDIR /app
COPY viaipe.py .
RUN pip install requests psycopg2
CMD ["python", "viaipe.py"]
