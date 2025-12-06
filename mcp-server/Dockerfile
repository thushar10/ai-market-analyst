FROM python:3.11-slim

WORKDIR /app

# System deps (if needed by yfinance/newsapi; usually not much is needed)
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

CMD ["python", "server.py"]