FROM python:3.11-slim

WORKDIR /app

# copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application
COPY SimpleLibrary.py .

# create logs directory
RUN mkdir -p /app/logs

# expose port
EXPOSE 8000

# container health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["python", "SimpleLibrary.py"]