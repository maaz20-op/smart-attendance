# ---------- BUILD STAGE ----------
FROM python:3.10-slim AS builder

WORKDIR /app

# Build dependencies (ONLY for compiling dlib and other ML libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Build wheels instead of installing directly
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---------- RUNTIME STAGE ----------
FROM python:3.10-slim

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache-dir /wheels/*

COPY . .

# Create storage directory
RUN mkdir -p ./storage/embeddings

# Expose port
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
