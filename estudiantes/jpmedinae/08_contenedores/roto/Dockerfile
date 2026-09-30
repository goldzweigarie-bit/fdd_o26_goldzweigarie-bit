FROM python:3.13.7-alpine3.22
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN adduser -D -u 10001 appuser
USER appuser
CMD ["python", "app.py"]
