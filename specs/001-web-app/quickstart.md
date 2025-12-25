# Quickstart: Web Application for Watermark Removal

**Feature**: 001-web-app  
**Date**: 2025-12-25  
**Purpose**: Step-by-step guide to run the web application locally and verify all user stories

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop**: Version 24+ (includes Docker Compose)
- **Git**: For cloning the repository
- **Node.js**: Version 18+ (for frontend development)
- **Python**: Version 3.11+ (for backend development without Docker)
- **Make** (optional): For simplified commands

**System Requirements**:
- **CPU**: 2 cores minimum (4 cores recommended for comfortable development)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 5GB for Docker images and build artifacts

---

## Quick Setup (Docker Compose - Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/allenk/GeminiWatermarkTool.git
cd GeminiWatermarkTool
git checkout 001-web-app
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp web/backend/.env.example web/backend/.env
cp web/frontend/.env.example web/frontend/.env

# Edit web/backend/.env
# Set TURNSTILE_SECRET_KEY=your_cloudflare_test_key

# Edit web/frontend/.env
# Set NEXT_PUBLIC_TURNSTILE_SITE_KEY=your_cloudflare_test_site_key
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Get Cloudflare Turnstile Keys**:
1. Visit https://dash.cloudflare.com/?to=/:account/turnstile
2. Create a new site (use `localhost` for development)
3. Copy **Site Key** → `NEXT_PUBLIC_TURNSTILE_SITE_KEY`
4. Copy **Secret Key** → `TURNSTILE_SECRET_KEY`

### Step 3: Build and Run

```bash
# Build all containers (this will take 5-10 minutes on first run)
docker-compose up --build

# Expected output:
# ✓ Builder container compiles GeminiWatermarkTool binary
# ✓ Backend container starts on http://localhost:8000
# ✓ Frontend container starts on http://localhost:3000
```

**Container Build Process**:
1. **Builder** (5-8 min): Installs CMake, vcpkg, compiles C++ GeminiWatermarkTool
2. **Backend** (1-2 min): Copies binary, installs Python dependencies (FastAPI, etc.)
3. **Frontend** (2-3 min): Installs Node.js dependencies, starts Next.js dev server

### Step 4: Verify Services

Open your browser and navigate to:

- **Frontend**: http://localhost:3000 (Next.js dev server with hot reload)
- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Backend Health Check**: http://localhost:8000/health (should return `{"status": "healthy"}`)

---

## User Story Validation

### User Story 1: Upload and Process Single Image (Priority: P1)

**Goal**: Test single image upload, processing, and download workflow

#### Test Steps:

1. **Open Application**:
   - Navigate to http://localhost:3000
   - Verify Material Design 3 UI loads (three-step layout visible)

2. **Complete Turnstile**:
   - Cloudflare Turnstile widget should be visible
   - Complete verification (may be invisible in development mode)

3. **Upload Image**:
   ```bash
   # Use a sample watermarked image
   # (You can generate one using the CLI tool or use a test image)
   
   # Drag and drop onto upload zone, OR
   # Click upload zone to open file picker
   ```

4. **Verify Processing**:
   - Material 3 circular progress indicator should appear
   - Processing should complete in < 5 seconds for 2MB images
   - Before/after comparison slider should display

5. **Download Result**:
   - Click "Download" button
   - Verify image downloads with watermark removed

**Expected Results**:
- ✓ Upload zone accepts JPG, PNG, WebP, BMP (< 10MB)
- ✓ Processing completes within 5 seconds (2MB image)
- ✓ Image preview shows watermark removed
- ✓ Download button provides processed image

**Validation Command** (Backend API):
```bash
curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test_image.jpg" \
  -F "turnstile_token=test_token_for_development" \
  --output result.json

# Check response
cat result.json | jq '.jobs[0].status'
# Should return: "completed"
```

---

### User Story 2: Bot Protection with Turnstile (Priority: P2)

**Goal**: Verify Turnstile integration blocks uploads without verification

#### Test Steps:

1. **Test Without Turnstile**:
   ```bash
   # Attempt upload without Turnstile token
   curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@test_image.jpg" \
     --output error.json
   
   # Check error response
   cat error.json | jq '.error'
   # Should return: "bad_request" (missing Turnstile token)
   ```

2. **Test With Invalid Turnstile**:
   ```bash
   # Attempt upload with invalid token
   curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@test_image.jpg" \
     -F "turnstile_token=invalid_token" \
     --output error.json
   
   # Check error response
   cat error.json | jq '.error'
   # Should return: "unauthorized" (Turnstile verification failed)
   ```

3. **Test Frontend Behavior**:
   - Attempt upload before completing Turnstile widget
   - Frontend should display error: "Please complete verification"

**Expected Results**:
- ✓ Uploads without Turnstile token are rejected (400 Bad Request)
- ✓ Uploads with invalid token are rejected (401 Unauthorized)
- ✓ Frontend displays clear error messages
- ✓ Valid Turnstile token allows processing

---

### User Story 3: Batch Image Processing (Priority: P3)

**Goal**: Test batch upload, parallel processing, and ZIP download

#### Test Steps:

1. **Prepare Test Images**:
   ```bash
   # Create a directory with 5 test images
   mkdir test_batch
   # Copy 5 watermarked images to test_batch/
   ```

2. **Upload Batch**:
   - Select multiple files (5 images) in file picker, OR
   - Drag and drop multiple files onto upload zone

3. **Monitor Processing**:
   - Progress indicator should show status for each image
   - Processing should complete in < 30 seconds for 10 images

4. **Download ZIP**:
   - "Download All as ZIP" button should appear
   - Click button to download ZIP archive
   - Extract ZIP and verify all images processed

**Validation Command** (Backend API):
```bash
curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test_batch/image1.jpg" \
  -F "files=@test_batch/image2.jpg" \
  -F "files=@test_batch/image3.jpg" \
  -F "files=@test_batch/image4.jpg" \
  -F "files=@test_batch/image5.jpg" \
  -F "turnstile_token=test_token_for_development" \
  --output batch_result.json

# Check batch response
cat batch_result.json | jq '{total: .total_jobs, successful: .successful_jobs, failed: .failed_jobs}'

# Download ZIP
SESSION_ID=$(cat batch_result.json | jq -r '.session_id')
curl "http://localhost:8000/api/v1/download/$SESSION_ID" --output processed_images.zip

# Verify ZIP contents
unzip -l processed_images.zip
```

**Expected Results**:
- ✓ Batch upload accepts 1-10 images per request
- ✓ All images process in parallel (< 30 seconds for 10 images)
- ✓ Failed images don't block others (resilience)
- ✓ ZIP download contains all successfully processed images

---

## Edge Case Validation

### Test 1: Unsupported File Format

```bash
curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test.gif" \
  -F "turnstile_token=test_token"

# Expected: 400 Bad Request
# Message: "Unsupported file format: GIF. Supported formats: JPG, JPEG, PNG, WebP, BMP"
```

### Test 2: File Size Exceeds Limit

```bash
# Create a large test file (> 10MB)
dd if=/dev/zero of=large_image.jpg bs=1M count=15

curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@large_image.jpg" \
  -F "turnstile_token=test_token"

# Expected: 400 Bad Request
# Message: "File size exceeds 10MB limit"
```

### Test 3: Rate Limiting

```bash
# Send 11 requests in quick succession
for i in {1..11}; do
  curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
    -H "Content-Type: multipart/form-data" \
    -F "files=@test_image.jpg" \
    -F "turnstile_token=test_token" &
done
wait

# Expected: 10 requests succeed (200 OK), 11th fails with 429 Too Many Requests
```

### Test 4: Image Without Watermark

```bash
# Upload a clean image (no watermark)
curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@clean_image.jpg" \
  -F "turnstile_token=test_token" \
  --output result.json

# Expected: 200 OK (processing succeeds)
# Warning in response: "No watermark detected; original image returned"
```

---

## Performance Benchmarks

### Single Image Processing

```bash
# Measure processing time for 2MB image
time curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@2mb_image.jpg" \
  -F "turnstile_token=test_token" \
  --output /dev/null

# Target: < 5 seconds total (upload + processing + download)
```

### Batch Processing

```bash
# Measure batch processing time for 10 images
time curl -X POST "http://localhost:8000/api/v1/remove-watermark" \
  -H "Content-Type: multipart/form-data" \
  $(for i in {1..10}; do echo "-F files=@test_batch/image${i}.jpg"; done) \
  -F "turnstile_token=test_token" \
  --output /dev/null

# Target: < 30 seconds for 10 images
```

### Concurrent Users

```bash
# Simulate 100 concurrent uploads
ab -n 100 -c 100 -p test_payload.txt -T "multipart/form-data" \
  "http://localhost:8000/api/v1/remove-watermark"

# Target: No failures, < 10s p95 latency
```

---

## Troubleshooting

### Issue: Frontend Cannot Reach Backend

**Symptom**: CORS errors in browser console

**Solution**:
```bash
# Check backend CORS configuration in web/backend/src/api/middleware.py
# Ensure ALLOWED_ORIGINS includes http://localhost:3000

# Restart backend container
docker-compose restart backend
```

### Issue: Binary Not Found Error

**Symptom**: Backend logs show "GeminiWatermarkTool binary not found"

**Solution**:
```bash
# Rebuild builder container to compile binary
docker-compose build --no-cache builder

# Verify binary was copied to backend container
docker-compose exec backend ls -la /app/bin/GeminiWatermarkTool

# If missing, rebuild entire stack
docker-compose down && docker-compose up --build
```

### Issue: Turnstile Verification Always Fails

**Symptom**: All uploads rejected with "Turnstile verification failed"

**Solution**:
```bash
# For development testing, set TURNSTILE_SECRET_KEY to test key
# In web/backend/.env:
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA

# This is Cloudflare's test secret key that always passes validation
```

### Issue: Images Not Deleted After Processing

**Symptom**: `/tmp/uploads` and `/tmp/outputs` directories growing

**Solution**:
```bash
# Check backend logs for cleanup task failures
docker-compose logs backend | grep "cleanup"

# Manually trigger cleanup (inside container)
docker-compose exec backend python -c "from src.services.file_service import cleanup_old_files; cleanup_old_files()"
```

---

## Stopping and Cleanup

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (cleans ephemeral storage)
docker-compose down -v

# Remove all images (free up disk space)
docker-compose down --rmi all
```

---

## Next Steps

After completing this quickstart:

1. **Review generated tasks**: `specs/001-web-app/tasks.md` (run `/speckit.tasks`)
2. **Read API contract**: `specs/001-web-app/contracts/api.openapi.yaml`
3. **Study data model**: `specs/001-web-app/data-model.md`
4. **Begin implementation**: Follow tasks.md in priority order (P1 → P2 → P3)

**Ready for production deployment?**
- See `deployment/kubernetes/` for GKE manifests
- See `deployment/cloudflare/wrangler.toml` for Cloudflare Pages config
- Review `specs/001-web-app/research.md` for deployment best practices

---

## Success Criteria Checklist

After completing this quickstart, verify:

- ✓ **SC-001**: 2MB image processes in < 5 seconds
- ✓ **SC-002**: 95%+ success rate on valid watermarked images
- ✓ **SC-003**: Frontend loads with LCP < 2.5s (check Lighthouse)
- ✓ **SC-004**: Upload-process-download workflow intuitive (user testing)
- ✓ **SC-005**: 100 concurrent users handled (load testing with `ab`)
- ✓ **SC-006**: Batch (10 images) completes in < 30 seconds
- ✓ **SC-007**: No files persist > 1 hour (check `/tmp` directories)
- ✓ **SC-008**: Lighthouse score 90+ (run audit)
- ✓ **SC-009**: Error responses < 500ms (check with `time curl`)
- ✓ **SC-010**: Turnstile blocks 99%+ bots (production monitoring)

**All user stories (P1-P3) validated!** Web application ready for implementation.
