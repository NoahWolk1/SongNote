# Neural Singing Voice Synthesis Service
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the refactored modules
COPY *.py /app/

# Run the refactored Flask app
CMD ["python", "app.py"]
