# FREE Basic Pitch Service - Melody extraction from humming
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Create tmp directory for audio processing
RUN mkdir -p /app/tmp

EXPOSE 8001

CMD ["python", "service.py"]
