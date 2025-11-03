FROM python:3.11-slim

WORKDIR /app

# Install system build dependencies required for some Python packages (cryptography)
RUN apt-get update && \
	apt-get install -y build-essential libssl-dev libffi-dev python3-dev cargo && \
	rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
	pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["python", "-u", "app.py"]
