FROM python:3.10-slim

# System dependencies for face_recognition / dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better cache)
COPY requirements.txt .

RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8001

ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=info

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
