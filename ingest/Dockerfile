FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY gbfs_ingest.py .
CMD ["python", "-u", "gbfs_ingest.py"]
