FROM python:3.9-slim

RUN pip install "dask[distributed]" pandas numpy boto3

WORKDIR /app
COPY test.py .

CMD ["python", "test.py"]
