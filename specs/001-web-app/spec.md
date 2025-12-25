# Feature Specification: Web Application for Watermark Removal

**Feature Branch**: `001-web-app`  
**Created**: 2025-12-25  
**Status**: Draft  
**Input**: User description: "build a python api to call the Gemini Watermark Tool. in order to build the Gemini Watermark Tool, we need to build it in a linux container. the result of the build will be used for the actual python api container. build the frontend according to the constitution and build it in next.js for seo purpose. we also need to have the turnstile like the https://lastsnap.opencloudapps.com/ . the label and text ideas refer to https://lastsnap.opencloudapps.com/ also."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload and Process Single Image (Priority: P1)

A user visits the web application, uploads a watermarked image through a drag-and-drop interface or file picker, and receives a cleaned image without the Gemini watermark.

**Why this priority**: This is the core value proposition - enabling watermark removal through a web interface without requiring users to download CLI tools or understand command-line operations. This single flow delivers immediate value.

**Independent Test**: Can be fully tested by uploading a watermarked image through the web interface and verifying the returned image has the watermark removed. This works independently without any batch processing or advanced features.

**Acceptance Scenarios**:

1. **Given** a user on the homepage, **When** they drag and drop a watermarked JPG/PNG/WebP image onto the upload area, **Then** the system displays a processing indicator and automatically processes the image
2. **Given** an image is successfully processed, **When** processing completes, **Then** the user sees a preview of the cleaned image with download and drag-to-save options
3. **Given** a user uploads a 2MB watermarked image, **When** the system processes it, **Then** processing completes within 5 seconds
4. **Given** a user on mobile device, **When** they tap the upload area, **Then** the native file picker opens allowing image selection from gallery or camera

---

### User Story 2 - Bot Protection with Turnstile (Priority: P2)

The system enforces strict Turnstile validation with enhanced error handling and UX improvements, building on the basic Turnstile integration from User Story 1. This ensures production-ready bot protection with comprehensive logging and user feedback.

**Why this priority**: Essential for production deployment to prevent abuse, but not required for initial MVP functionality testing. User Story 1 includes basic Turnstile integration; this phase adds mandatory enforcement, detailed error handling, and UX enhancements (loading states, expiration handling, visual feedback).

**Independent Test**: Can be tested independently by attempting uploads with and without completing Turnstile verification, ensuring blocked requests return appropriate error messages.

**Acceptance Scenarios**:

1. **Given** a user on the homepage, **When** the page loads, **Then** a Cloudflare Turnstile widget is displayed in the upload area
2. **Given** a user has not completed Turnstile verification, **When** they attempt to upload an image, **Then** the system displays an error message prompting them to complete verification
3. **Given** a user has completed Turnstile verification, **When** they upload an image, **Then** the system proceeds with processing
4. **Given** a Turnstile token expires after 5 minutes, **When** the user attempts upload, **Then** the system prompts for re-verification

---

### User Story 3 - Batch Image Processing (Priority: P3)

Users can upload multiple watermarked images simultaneously and download all processed images as a ZIP archive, streamlining workflows for users with many images to clean.

**Why this priority**: Valuable for power users but not essential for initial launch. Single image processing (P1) already delivers core value. This enhances user experience for advanced scenarios.

**Independent Test**: Can be tested independently by uploading multiple images at once and verifying all are processed correctly with results bundled in a ZIP file.

**Acceptance Scenarios**:

1. **Given** a user on the upload page, **When** they select multiple images (up to 10), **Then** the system displays a progress indicator showing processing status for each image
2. **Given** multiple images are being processed, **When** all processing completes, **Then** the system offers a "Download All as ZIP" button
3. **Given** a user has uploaded 10 images totaling 20MB, **When** processing completes, **Then** all operations finish within 30 seconds
4. **Given** batch processing is in progress, **When** one image fails to process, **Then** the system continues processing remaining images and reports the error for the failed image only

---

### Edge Cases

- What happens when a user uploads an image without a Gemini watermark?
  - System should detect absence of watermark and return the original image with a warning message
- What happens when a user uploads an unsupported file format (e.g., GIF, TIFF)?
  - System rejects the upload with a clear error message listing supported formats: JPG, JPEG, PNG, WebP, BMP
- What happens when a user uploads an extremely large image (e.g., 50MB, 8K resolution)?
  - System enforces maximum file size limit (10MB default) and displays error message with size limit
- What happens when the watermark removal process fails due to corrupted image data?
  - System returns an error message explaining the failure and suggesting the user try the CLI tool for advanced troubleshooting
- What happens when backend API is unavailable or times out?
  - Frontend displays user-friendly error message and suggests retrying after a brief wait
- What happens when a user's network connection drops during upload?
  - System detects the interruption and displays appropriate reconnection message

## Requirements *(mandatory)*

### Functional Requirements

#### Frontend (Next.js)

- **FR-001**: System MUST provide a responsive web interface following Google Material Design 3 guidelines with explicit breakpoints: mobile (< 768px), tablet (768px-1024px), desktop (> 1024px)
- **FR-002**: System MUST implement a three-step workflow layout:
  1. Upload area with drag-and-drop and file picker
  2. Processing indicator showing progress
  3. Download/preview area with save options
- **FR-003**: System MUST integrate Cloudflare Turnstile widget for bot protection before allowing uploads
- **FR-004**: System MUST support image upload via drag-and-drop and file picker click; SHOULD support paste from clipboard (post-MVP enhancement)
- **FR-005**: System MUST display real-time processing status with Material 3 circular progress indicator
- **FR-006**: System MUST show image preview with before/after comparison slider after processing completes
- **FR-007**: System MUST support server-side rendering (SSR) for SEO optimization of landing page; documentation pages MAY use static generation
- **FR-008**: System MUST implement Material You dynamic color theming
- **FR-009**: Frontend MUST meet WCAG 2.1 AA accessibility standards
- **FR-010**: System MUST display clear, user-friendly error messages for failed uploads or processing errors

#### Backend (FastAPI)

- **FR-011**: System MUST provide a RESTful API endpoint accepting image uploads (POST /api/v1/remove-watermark)
- **FR-012**: System MUST accept image formats: JPEG (extensions: .jpg, .jpeg), PNG, WebP, BMP
- **FR-013**: System MUST validate Turnstile token before processing image uploads
- **FR-014**: System MUST invoke the compiled GeminiWatermarkTool binary to process images
- **FR-015**: System MUST return processed images with appropriate content-type headers
- **FR-016**: System MUST enforce rate limiting (10 requests per minute per IP address)
- **FR-016a**: Rate limit applies globally across all API endpoints per IP address (health checks excluded)
- **FR-016b**: System MUST return X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers in all API responses
- **FR-016c**: Turnstile verification requests do not count toward rate limit quota
- **FR-017**: System MUST delete uploaded images after processing completes (maximum retention: 1 hour for failed cleanup)
- **FR-018**: System MUST log all processing requests with anonymized IP addresses
- **FR-019**: System MUST return appropriate HTTP status codes (200 OK, 400 Bad Request, 429 Too Many Requests, 500 Internal Server Error)
- **FR-020**: System MUST auto-detect watermark size (small_48x48 or large_96x96 per data-model.md enum) using the same logic as CLI tool

#### Container Architecture

- **FR-021**: GeminiWatermarkTool MUST be compiled in a dedicated Linux build container with all C++ dependencies (CMake, vcpkg, OpenCV, etc.)
- **FR-022**: Compiled binary MUST be extracted from build container and copied into the Backend (FastAPI) runtime container
- **FR-023**: Backend (FastAPI) container MUST be lightweight (Alpine Linux base) with only Python runtime and required packages
- **FR-024**: Both containers MUST be orchestrated using Docker Compose for development environment
- **FR-025**: Production deployment MUST use multi-stage Docker builds to minimize final image size

#### Infrastructure

- **FR-026**: System MUST support separate development and production environment configurations
- **FR-027**: Production backend MUST be deployable to Google Kubernetes Engine (GKE)
- **FR-028**: Production frontend MUST be deployable to Cloudflare Pages
- **FR-029**: System MUST store temporary uploaded images in ephemeral storage (not persistent volumes)
- **FR-030**: System MUST expose health check endpoints (/health, /readiness) for Kubernetes probes

### Key Entities *(include if feature involves data)*

- **Upload Session**: Represents a single user upload request, including uploaded image data, Turnstile token, processing status, timestamp, and anonymized IP address
- **Processing Job**: Represents the watermark removal operation, including input image path, output image path, processing status (pending/processing/completed/failed), error messages (if any), and processing duration metrics
- **Image Metadata**: Contains image dimensions, file size, detected watermark size (small_48x48 or large_96x96 enum per data-model.md), file format, and validation status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload and process a watermarked image receiving cleaned output in under 5 seconds for images up to 2MB
- **SC-002**: System successfully processes 95% of uploads with valid Gemini watermarks on first attempt
- **SC-003**: Web interface loads with Core Web Vitals passing thresholds (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- **SC-004**: 90% of first-time users successfully complete the upload-process-download workflow without assistance
- **SC-005**: System handles 100 concurrent users processing images simultaneously without degradation
- **SC-006**: Batch processing of 10 images completes within 30 seconds
- **SC-007**: Zero user-uploaded images persist on server storage beyond 1 hour after processing
- **SC-008**: Frontend achieves Google Lighthouse score of 90+ for Performance, Accessibility, Best Practices, and SEO
- **SC-009**: API returns appropriate error messages within 500ms for invalid requests (wrong format, missing Turnstile, etc.)
- **SC-010**: System successfully blocks 99% of automated bot attempts via Turnstile integration

## Assumptions *(optional - document informed guesses)*

- Users will primarily upload images in common web formats (JPG, PNG) rather than specialized formats
- Average image size will be 1-3MB (typical smartphone/screenshot resolution)
- Most users will process 1-5 images per session
- Cloudflare Turnstile will be configured with "Managed" challenge mode balancing security and UX
- Backend API will be deployed with auto-scaling enabled (2-10 pods based on load)
- Frontend will use Next.js 14+ with App Router for optimal SSR and SEO
- Material 3 will be implemented using Material Web Components or Next.js-compatible library
- Processing container will have sufficient CPU/memory resources (2 CPU cores, 2GB RAM minimum per pod)
- Users understand they should backup original images before processing (per disclaimer)

## Out of Scope *(optional - explicitly excluded)*

- User authentication or account creation (stateless API only)
- Persistent storage of user images or processing history
- Payment processing or premium tiers
- Image editing features beyond watermark removal (crop, resize, filters, etc.)
- Support for video watermark removal
- Integration with cloud storage providers (Dropbox, Google Drive, etc.)
- Mobile native applications (iOS/Android apps) - web-only for MVP
- Real-time collaborative editing or sharing features
- Removal of invisible/steganographic watermarks (only visible Gemini watermarks)
