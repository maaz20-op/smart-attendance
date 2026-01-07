# ML Face Service Setup Guide

## What Was Fixed

The ml-face-service had several missing components that prevented it from working:

1. **Missing Storage Module** ✅ Fixed
   - Created `app/storage/embeddings.py` with `EmbeddingsStorage` class
   - Implements local JSON-based storage for face embeddings
   - Supports multiple embeddings per student

2. **Missing Configuration** ✅ Fixed
   - Created `.env.example` with all required settings
   - Configured for local storage path, thresholds, and server settings

3. **Missing Docker Setup** ✅ Fixed
   - Created `Dockerfile` with multi-stage build (similar to backend)
   - Handles dlib compilation in build stage
   - Minimal runtime dependencies

4. **Missing Git Configuration** ✅ Fixed
   - Created `.gitignore` for Python artifacts and local data
   - Created `.dockerignore` for efficient Docker builds
   - Added `.gitkeep` to preserve directory structure

## Architecture

The ml-face-service stores face embeddings **locally** in JSON files, NOT in MongoDB:

```
ml-face-service/
├── storage/
│   └── embeddings/
│       ├── {student_id1}.json    # Each student gets a file
│       ├── {student_id2}.json
│       └── ...
```

Each JSON file contains an array of 128-dimensional embeddings:
```json
[
  [0.123, 0.456, ..., 0.789],  # First embedding
  [0.234, 0.567, ..., 0.890]   # Second embedding (different angle)
]
```

## Setup Instructions

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential cmake

# macOS
brew install cmake
```

### Installation

```bash
# 1. Navigate to ml-face-service
cd ml-face-service

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies (may take 5-10 minutes due to dlib)
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env if needed (defaults work fine)

# 5. Run the service
python -m app.main
```

The service will start on `http://localhost:8001`

### Verify Installation

```bash
# Check health endpoint
curl http://localhost:8001/api/face/health

# Expected response:
# {"status":"healthy","service":"ml-face-recognition"}
```

## Usage with Backend API

The backend-api communicates with this service via HTTP:

### 1. Configure Backend API

In `backend-api/.env`:
```env
ML_SERVICE_URL=http://localhost:8001
```

### 2. Start Both Services

```bash
# Terminal 1: ML Service
cd ml-face-service
source .venv/bin/activate
python -m app.main

# Terminal 2: Backend API
cd backend-api
source .venv/bin/activate
python -m app.main

# Terminal 3: Frontend
cd frontend
npm run dev
```

### 3. Test Face Registration

When a student uploads a photo via the frontend:
1. Frontend → `POST /students/me/face-image` → Backend API
2. Backend API → `POST /api/face/register-face` → ML Service
3. ML Service extracts embedding and saves to `storage/embeddings/{student_id}.json`
4. Backend API uploads image to Cloudinary
5. Backend API marks student as `verified: true` in MongoDB

### 4. Test Attendance Marking

When a teacher marks attendance:
1. Frontend → `POST /api/attendance/mark` → Backend API
2. Backend API → `POST /api/face/recognize-face` → ML Service
3. ML Service detects faces and matches against stored embeddings
4. ML Service returns matched student IDs
5. Backend API enriches with student details from MongoDB
6. Frontend displays results for confirmation

## API Endpoints

### Register Face
```http
POST http://localhost:8001/api/face/register-face
Content-Type: multipart/form-data

file: <image file>
student_id: "user_object_id"
```

### Register Face (Base64)
```http
POST http://localhost:8001/api/face/register-face-base64
Content-Type: application/json

{
  "student_id": "user_object_id",
  "image_base64": "data:image/jpeg;base64,..."
}
```

### Recognize Faces
```http
POST http://localhost:8001/api/face/recognize-face
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,...",
  "student_ids": ["id1", "id2"]  // optional filter
}
```

**Response:**
```json
{
  "faces": [
    {
      "student_id": "user_id",
      "confidence": 0.95,
      "distance": 0.42,
      "status": "present",
      "box": {"top": 100, "right": 300, "bottom": 400, "left": 100}
    }
  ],
  "count": 1
}
```

### Delete Embeddings
```http
DELETE http://localhost:8001/api/face/embeddings/{student_id}
```

### Health Check
```http
GET http://localhost:8001/api/face/health
```

## Configuration Options

Edit `.env` to customize:

```env
# Server
ML_SERVICE_HOST=0.0.0.0
ML_SERVICE_PORT=8001

# Face Recognition
MIN_FACE_AREA_RATIO=0.05      # Minimum face size (5% of image)
NUM_JITTERS=5                 # Embedding quality (1-10, higher = better but slower)
CONFIDENCE_THRESHOLD=0.50     # Distance threshold for "present"
UNCERTAIN_THRESHOLD=0.60      # Distance threshold for "uncertain"

# Storage
EMBEDDINGS_STORAGE_PATH=./storage/embeddings
```

## Docker Build (Optional)

**Note:** The Dockerfile is provided but the service is meant to run locally. Docker build may have SSL certificate issues in some environments.

```bash
# Build image
cd ml-face-service
docker build -t ml-face-service .

# Run container
docker run -p 8001:8001 -v $(pwd)/storage:/app/storage ml-face-service
```

## Troubleshooting

### dlib installation fails
```bash
# Ensure CMake and build tools are installed
sudo apt-get install build-essential cmake

# Or try installing dlib separately
pip install dlib
```

### "No face detected" error
- Ensure good lighting in the photo
- Face should be clearly visible
- Face should cover at least 5% of image
- Try increasing MIN_FACE_AREA_RATIO in .env

### "Multiple faces detected" during registration
- Ensure only one person's face is visible in registration photo
- For attendance marking, this is normal and handled

### Service not starting
```bash
# Check if port 8001 is already in use
lsof -i :8001

# Or run on different port
ML_SERVICE_PORT=8002 python -m app.main
```

### Low recognition accuracy
- Register multiple photos per student (different angles)
- Ensure good image quality
- Adjust CONFIDENCE_THRESHOLD in .env

## Storage Management

### Backup Embeddings
```bash
# Backup all embeddings
tar -czf embeddings-backup-$(date +%Y%m%d).tar.gz storage/embeddings/
```

### Restore Embeddings
```bash
# Restore from backup
tar -xzf embeddings-backup-20250107.tar.gz
```

### Clear All Embeddings
```bash
# Remove all student embeddings
rm storage/embeddings/*.json
```

### View Student Embeddings
```bash
# View embeddings for a specific student
cat storage/embeddings/{student_id}.json | python -m json.tool
```

## Performance

- **Face detection**: ~0.5-2 seconds per image (CPU)
- **Face matching**: ~0.1 seconds for 100 students
- **Memory usage**: ~500MB
- **Startup time**: ~10 seconds

Scales well for small-medium deployments (<500 students).

## Security Notes

- This service should ONLY run on localhost or trusted local network
- No authentication is implemented (assumes trusted environment)
- CORS allows all origins (for local development)
- Do NOT expose to public internet

## Additional Resources

- [Architecture Overview](../ARCHITECTURE.md)
- [Migration Guide](../MIGRATION.md)
- [Backend API Documentation](../backend-api/README.md)
- [Main README](../README.md)

## Support

If you encounter issues:
1. Check this guide first
2. Review [ml-face-service/README.md](./README.md)
3. Check [GitHub Issues](https://github.com/nem-web/smart-attendance/issues)
4. Consult [ARCHITECTURE.md](../ARCHITECTURE.md) for system design
