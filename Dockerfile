FROM python:3.13.6-alpine3.21
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["python", "src/main.py"]