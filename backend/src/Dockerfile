FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

RUN mkdir -p uploads

WORKDIR /app

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]