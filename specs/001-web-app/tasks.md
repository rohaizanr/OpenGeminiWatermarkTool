# Tasks: Web Application for Watermark Removal

**Feature Branch**: `001-web-app`  
**Input**: Design documents from `/specs/001-web-app/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.openapi.yaml, quickstart.md

**Tests**: Tests are NOT explicitly requested in the feature specification. Therefore, NO test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **Checkbox**: ALWAYS starts with `- [ ]`
- **[TaskID]**: Sequential ID (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses web application structure:
- **Backend**: `web/backend/src/`
- **Frontend**: `web/frontend/src/`
- **Build**: `build/`
- **Deployment**: `deployment/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create web application directory structure: `web/`, `web/frontend/`, `web/backend/`, `build/`, `deployment/`
- [X] T002 [P] Initialize Python backend project in `web/backend/`: create `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`
- [X] T003 [P] Initialize Next.js frontend project in `web/frontend/`: run `npx create-next-app@latest` with TypeScript and App Router
- [X] T004 [P] Create Docker build container Dockerfile in `build/Dockerfile.builder` for compiling C++ GeminiWatermarkTool binary
- [X] T005 Create Docker Compose configuration in `docker-compose.yml` for development environment (frontend, backend, builder services)
- [X] T006 [P] Configure backend linting tools in `web/backend/pyproject.toml`: black, mypy, flake8
- [X] T007 [P] Configure frontend linting tools in `web/frontend/`: ESLint, Prettier for TypeScript
- [X] T008 Create environment file templates: `web/backend/.env.example`, `web/frontend/.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Binary Compilation Infrastructure

- [X] T009 Implement C++ build stage in `build/Dockerfile.builder`: install CMake, vcpkg, GCC, compile GeminiWatermarkTool with static linking
- [X] T010 Create backend Dockerfile in `web/backend/Dockerfile`: use Alpine base, copy binary from builder, install Python dependencies
- [X] T011 Configure Docker Compose to orchestrate builder → backend binary copy in `docker-compose.yml`

### Backend Core Infrastructure

- [X] T012 Create FastAPI application entry point in `web/backend/src/main.py`: initialize app, configure CORS, register routes
- [X] T013 Implement configuration management in `web/backend/src/core/config.py`: environment variables (dev/prod), Turnstile keys, rate limits
- [X] T014 [P] Implement structured logging in `web/backend/src/core/logging.py`: JSON logs, anonymized IP addresses, request tracing
- [X] T015 [P] Implement custom exceptions in `web/backend/src/core/exceptions.py`: ValidationError, TurnstileError, ProcessingError, RateLimitError
- [X] T016 Create CORS middleware in `web/backend/src/api/middleware.py`: allow frontend origin, handle preflight requests
- [X] T017 Implement rate limiting middleware in `web/backend/src/api/middleware.py`: slowapi integration, 10 req/min per IP
- [X] T018 [P] Implement health check endpoints in `web/backend/src/api/routes.py`: GET /health, GET /readiness (verify binary exists)
- [X] T019 Create Pydantic base models in `web/backend/src/api/models.py`: ErrorResponse schema per OpenAPI spec

### Backend Services Foundation

- [X] T020 [P] Implement binary executor utility in `web/backend/src/utils/binary_executor.py`: subprocess wrapper, timeout handling, exit code parsing
- [X] T021 [P] Implement file validators in `web/backend/src/utils/validators.py`: image format validation, file size limits, MIME type detection
- [X] T022 Implement file service in `web/backend/src/services/file_service.py`: ephemeral storage management, UUID filename generation, cleanup tasks

### Frontend Core Infrastructure

- [X] T023 Configure Material Design 3 theming in `web/frontend/src/styles/theme.ts`: Material You color tokens, elevation system
- [X] T024 Create root layout in `web/frontend/src/app/layout.tsx`: Material 3 provider, global styles, metadata for SEO
- [X] T025 Configure Tailwind CSS in `web/frontend/tailwind.config.js`: integrate Material 3 utility classes
- [X] T026 [P] Create API client service in `web/frontend/src/services/watermarkApi.ts`: axios/fetch wrapper, error handling, base URL config
- [X] T027 [P] Create TypeScript types in `web/frontend/src/types/api.ts`: match OpenAPI schemas (ProcessingJob, ErrorResponse, etc.)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload and Process Single Image (Priority: P1) 🎯 MVP

**Goal**: Enable users to upload a watermarked image through drag-and-drop, process it via the backend API, and download the cleaned result in under 5 seconds.

**Independent Test**: Upload a 2MB watermarked JPG through the web interface and verify the processed image downloads without watermark in < 5 seconds.

### Backend - Data Models (User Story 1)

- [X] T028 [P] [US1] Create Upload Session model in `web/backend/src/api/models.py`: session_id, client_ip (anonymized), turnstile_token, uploaded_at per data-model.md
- [X] T029 [P] [US1] Create Processing Job model in `web/backend/src/api/models.py`: job_id, session_id, status enum, file paths, duration_ms, watermark_size enum per data-model.md
- [X] T030 [P] [US1] Create Image Metadata model in `web/backend/src/api/models.py`: file_name, file_size_bytes, dimensions, format enum, validation_passed per data-model.md

### Backend - Services (User Story 1)

- [X] T031 [US1] Implement Turnstile verification service in `web/backend/src/services/turnstile_service.py`: httpx POST to Cloudflare API, token validation, error handling
- [X] T032 [US1] Implement watermark service in `web/backend/src/services/watermark_service.py`: orchestrate upload → validation → binary execution → response, integrate file_service and binary_executor

### Backend - API Endpoint (User Story 1)

- [X] T033 [US1] Implement POST /api/v1/remove-watermark endpoint in `web/backend/src/api/routes.py`: handle single file upload, validate Turnstile token, return processed image as base64
- [X] T034 [US1] Add request validation in POST /api/v1/remove-watermark: check file format (JPG/PNG/WebP/BMP), enforce 10MB limit, return 400 errors per OpenAPI spec
- [X] T035 [US1] Add response handling in POST /api/v1/remove-watermark: return SingleImageResponse schema with processed_image_base64, duration_ms, watermark_size
- [X] T036 [US1] Implement error responses in POST /api/v1/remove-watermark: 400 (bad request), 401 (Turnstile failed), 500 (processing error), 504 (timeout) per OpenAPI spec
- [X] T037 [US1] Add background cleanup task in POST /api/v1/remove-watermark: delete uploaded/processed files after response sent using FastAPI BackgroundTasks

### Frontend - UI Components (User Story 1)

- [X] T038 [P] [US1] Create TurnstileWidget component in `web/frontend/src/components/TurnstileWidget.tsx`: embed Cloudflare Turnstile SDK, expose token callback
- [X] T039 [P] [US1] Create UploadZone component in `web/frontend/src/components/UploadZone.tsx`: drag-and-drop area, file picker click, accept JPG/PNG/WebP/BMP, validate 10MB limit
- [X] T040 [P] [US1] Create ProcessingIndicator component in `web/frontend/src/components/ProcessingIndicator.tsx`: Material 3 circular progress, show processing status
- [X] T041 [P] [US1] Create ImagePreview component in `web/frontend/src/components/ImagePreview.tsx`: display processed image, before/after comparison slider (optional for MVP)

### Frontend - Page Integration (User Story 1)

- [X] T042 [US1] Implement homepage in `web/frontend/src/app/page.tsx`: three-step workflow (upload → process → download), integrate TurnstileWidget, UploadZone, ProcessingIndicator, ImagePreview
- [X] T043 [US1] Add upload logic in `web/frontend/src/app/page.tsx`: collect Turnstile token, call POST /api/v1/remove-watermark with FormData, handle loading state
- [X] T044 [US1] Add download logic in `web/frontend/src/app/page.tsx`: decode base64 image from API response, trigger browser download with filename
- [X] T045 [US1] Add error handling in `web/frontend/src/app/page.tsx`: display Material 3 snackbar for 400/401/500 errors, show user-friendly messages per spec.md edge cases

### Frontend - Accessibility & Responsiveness (User Story 1)

- [X] T046 [US1] Implement mobile-responsive layout in `web/frontend/src/app/page.tsx`: breakpoints for mobile/tablet/desktop, test drag-and-drop on touch devices
- [X] T047 [US1] Add ARIA labels and keyboard navigation in UploadZone component: ensure WCAG 2.1 AA compliance per plan.md
- [X] T048 [US1] Test Core Web Vitals in `web/frontend/`: run Lighthouse audit, ensure LCP < 2.5s, FID < 100ms, CLS < 0.1 per spec.md success criteria SC-003

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can upload a single image, see processing indicator, and download the cleaned result. This is the MVP!

---

## Phase 4: User Story 2 - Bot Protection with Turnstile (Priority: P2)

**Goal**: Enforce Cloudflare Turnstile verification before allowing uploads to prevent automated abuse and ensure only legitimate users can process images.

**Independent Test**: Attempt upload without completing Turnstile verification and verify the request is blocked with 401 Unauthorized. Complete verification and verify upload proceeds successfully.

### Backend - Turnstile Enforcement (User Story 2)

- [ ] T049 [US2] Enhance mandatory Turnstile validation in POST /api/v1/remove-watermark: ensure stricter enforcement with explicit rejection if turnstile_token missing (400) or verification fails (401), add validation checks before any processing
- [ ] T050 [US2] Enhance Turnstile error handling in `web/backend/src/services/turnstile_service.py`: expand error parsing to cover all Cloudflare API error codes (timeout-or-duplicate, invalid-input-response, etc.), return specific user-friendly error messages per OpenAPI spec
- [ ] T051 [US2] Add Turnstile verification logging in `web/backend/src/services/turnstile_service.py`: log verification attempts, success/failure rates, anonymized IPs

### Frontend - Turnstile UI/UX (User Story 2)

- [ ] T052 [US2] Add Turnstile loading state in `web/frontend/src/components/TurnstileWidget.tsx`: show loading indicator while widget initializes
- [ ] T053 [US2] Implement Turnstile error feedback in `web/frontend/src/app/page.tsx`: display "Please complete verification" message if token missing or expired
- [ ] T054 [US2] Add Turnstile re-verification logic in `web/frontend/src/app/page.tsx`: detect 5-minute token expiration, trigger re-challenge automatically
- [ ] T055 [US2] Add visual feedback in UploadZone: disable upload area until Turnstile verified, show lock icon or "Verify to Upload" message

### Configuration & Testing (User Story 2)

- [ ] T056 [US2] Configure Turnstile keys in environment files: add TURNSTILE_SECRET_KEY to `web/backend/.env`, NEXT_PUBLIC_TURNSTILE_SITE_KEY to `web/frontend/.env`
- [ ] T057 [US2] Document Turnstile setup in quickstart.md: instructions to get test keys from Cloudflare dashboard, localhost domain setup

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Single image upload requires Turnstile verification, blocking bots effectively.

---

## Phase 5: User Story 3 - Batch Image Processing (Priority: P3)

**Goal**: Enable users to upload multiple images (up to 10) simultaneously and download all processed results as a ZIP archive in under 30 seconds.

**Independent Test**: Upload 5 watermarked images at once, verify all process in parallel, and download the ZIP containing all cleaned images.

### Backend - Batch Processing Logic (User Story 3)

- [ ] T058 [US3] Update POST /api/v1/remove-watermark to handle multiple files: modify request handler to accept files[] array (1-10 files) per OpenAPI spec
- [ ] T059 [US3] Implement parallel processing in `web/backend/src/services/watermark_service.py`: use asyncio.gather() to process multiple images concurrently
- [ ] T060 [US3] Update response schema in POST /api/v1/remove-watermark: return BatchImageResponse when multiple files uploaded (total_jobs, successful_jobs, failed_jobs)
- [ ] T061 [US3] Add batch resilience in `web/backend/src/services/watermark_service.py`: continue processing remaining images if one fails, populate error_message for failed jobs

### Backend - ZIP Download Endpoint (User Story 3)

- [ ] T062 [P] [US3] Implement GET /api/v1/download/{session_id} endpoint in `web/backend/src/api/routes.py`: create ZIP archive from processed images in session
- [ ] T063 [US3] Implement ZIP creation logic in `web/backend/src/services/file_service.py`: use zipfile module, add all processed images from session_id directory
- [ ] T064 [US3] Add ZIP cleanup in `web/backend/src/services/file_service.py`: delete ZIP file and session directory after download or 1-hour timeout
- [ ] T065 [US3] Handle 404 errors in GET /api/v1/download/{session_id}: return ErrorResponse if session not found or expired per OpenAPI spec

### Frontend - Batch Upload UI (User Story 3)

- [ ] T066 [US3] Update UploadZone component to handle multiple file selection: modify file input to accept multiple="true", validate 1-10 file limit
- [ ] T067 [US3] Create BatchProgressIndicator component in `web/frontend/src/components/BatchProgressIndicator.tsx`: show progress for each image (pending/processing/completed/failed)
- [ ] T068 [US3] Update ImagePreview component to display batch results: show thumbnails of all processed images, indicate failed items with error icons
- [ ] T069 [US3] Add "Download All as ZIP" button in `web/frontend/src/app/page.tsx`: call GET /api/v1/download/{session_id}, trigger browser download

### Frontend - Batch Processing Logic (User Story 3)

- [ ] T070 [US3] Update upload logic in `web/frontend/src/app/page.tsx`: send all selected files in single FormData request to POST /api/v1/remove-watermark
- [ ] T071 [US3] Handle BatchImageResponse in `web/frontend/src/app/page.tsx`: parse total/successful/failed counts, display summary to user
- [ ] T072 [US3] Implement download ZIP logic in `web/frontend/src/services/watermarkApi.ts`: fetch ZIP from download_url, convert blob to download link
- [ ] T073 [US3] Add batch error handling in `web/frontend/src/app/page.tsx`: show which images failed, allow retry for failed items individually

**Checkpoint**: All user stories (P1, P2, P3) should now be independently functional. Single and batch uploads work with Turnstile protection and ZIP download.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [ ] T074 [P] Create API documentation in `web/backend/README.md`: setup instructions, environment variables, Docker Compose usage
- [ ] T075 [P] Create frontend documentation in `web/frontend/README.md`: development setup, Material 3 component usage, deployment to Cloudflare Pages
- [ ] T076 [P] Update root README.md: add web application section with quickstart link, deployment instructions

### Performance Optimization

- [ ] T077 [P] Optimize frontend bundle size: analyze Next.js build output, implement dynamic imports for large components (ImagePreview comparison slider)
- [ ] T078 [P] Add frontend caching in `web/frontend/src/services/watermarkApi.ts`: implement request deduplication for repeated uploads
- [ ] T079 Optimize backend memory usage in `web/backend/src/services/watermark_service.py`: stream large files instead of loading entirely into memory

### Security Hardening

- [ ] T080 [P] Add input sanitization in `web/backend/src/utils/validators.py`: validate filename characters, prevent path traversal attacks
- [ ] T081 [P] Implement HTTPS-only enforcement in `web/backend/src/api/middleware.py`: redirect HTTP to HTTPS in production
- [ ] T082 Add security headers in `web/backend/src/api/middleware.py`: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options

### Deployment Configuration

- [ ] T083 [P] Create Kubernetes deployment manifests in `deployment/kubernetes/deployment.yaml`: define backend deployment with 2-10 replicas, resource limits (2 CPU, 2GB RAM)
- [ ] T084 [P] Create Kubernetes service manifest in `deployment/kubernetes/service.yaml`: LoadBalancer type, expose port 8000
- [ ] T085 [P] Create Kubernetes HPA manifest in `deployment/kubernetes/hpa.yaml`: horizontal pod autoscaler with CPU 70%, memory 80% targets
- [ ] T086 [P] Create Kubernetes ConfigMap in `deployment/kubernetes/configmap.yaml`: non-sensitive config (API URLs, rate limits)
- [ ] T087 [P] Create Kubernetes Secret template in `deployment/kubernetes/secret.yaml.template`: Turnstile secret key placeholder (actual secret in GCP Secret Manager)
- [ ] T088 [P] Create Cloudflare Pages config in `deployment/cloudflare/wrangler.toml`: build command, environment variables, custom domain
- [ ] T089 Create Terraform configuration in `deployment/terraform/main.tf`: provision GKE cluster, node pools, networking (optional for infrastructure as code)

### Final Validation

- [ ] T090 Run full quickstart validation in `specs/001-web-app/quickstart.md`: verify all user stories (P1, P2, P3) work end-to-end
- [ ] T091 Run performance benchmarks per quickstart.md: single image < 5s, batch 10 images < 30s, 100 concurrent users
- [ ] T092 Run Lighthouse audit on frontend: verify Core Web Vitals targets (LCP < 2.5s, FID < 100ms, CLS < 0.1, score 90+)
- [ ] T093 Verify constitution compliance: check all 7 principles (cross-platform, mathematical correctness, UX, Material 3, dual env, zero dependencies, security)
- [ ] T094 Verify ephemeral storage cleanup policy: confirm uploaded/processed files are deleted within 1 hour by monitoring /tmp/uploads and /tmp/outputs directories, validate background cleanup tasks execute successfully per SC-007

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: No dependencies - can start immediately
2. **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
3. **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP foundation
4. **User Story 2 (Phase 4)**: Depends on Foundational + US1 completion (modifies US1 endpoint)
5. **User Story 3 (Phase 5)**: Depends on Foundational + US1 completion (extends US1 endpoint)
6. **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 backend endpoint exists (T033-T037) - Adds Turnstile validation to existing endpoint
- **User Story 3 (P3)**: Can start after US1 backend endpoint exists (T033-T037) - Extends endpoint for batch processing

**Note**: While US2 and US3 have sequential dependencies on US1's API endpoint, their frontend components can be developed in parallel with US1.

### Within Each User Story

**User Story 1**:
1. Models (T028-T030) → can run in parallel
2. Services (T031-T032) → depends on models
3. API endpoint (T033-T037) → depends on services
4. Frontend components (T038-T041) → can run in parallel with backend
5. Page integration (T042-T045) → depends on components
6. Accessibility (T046-T048) → depends on page integration

**User Story 2**:
1. Backend enforcement (T049-T051) → depends on US1 endpoint (T033)
2. Frontend Turnstile UI (T052-T055) → can run in parallel with backend
3. Configuration (T056-T057) → can run anytime

**User Story 3**:
1. Backend batch logic (T058-T061) → depends on US1 endpoint (T033)
2. ZIP endpoint (T062-T065) → can run in parallel with batch logic
3. Frontend batch UI (T066-T069) → can run in parallel with backend
4. Frontend logic (T070-T073) → depends on batch UI components

### Parallel Opportunities

**Phase 1 - Setup** (All can run in parallel):
- T002: Python backend init
- T003: Next.js frontend init
- T004: Docker builder Dockerfile
- T006: Backend linting
- T007: Frontend linting

**Phase 2 - Foundational** (Groups can run in parallel):
- **Binary**: T009-T011 (sequential within group)
- **Backend Core**: T012-T019 (T014-T015 parallel, rest sequential)
- **Backend Services**: T020-T022 (all parallel)
- **Frontend Core**: T023-T027 (T026-T027 parallel, T023-T025 sequential)

**Phase 3 - User Story 1** (Groups can run in parallel after dependencies met):
- **Models**: T028-T030 (all parallel)
- **Services**: T031 parallel with T032 (after models)
- **API endpoint**: T033-T037 (sequential, after services)
- **Frontend components**: T038-T041 (all parallel, independent of backend)
- **Page integration**: T042-T045 (sequential, after components)
- **Accessibility**: T046-T048 (sequential, after page)

**Phase 4 - User Story 2**:
- T049-T051: Backend enforcement (sequential)
- T052-T055: Frontend UI (parallel with backend)
- T056-T057: Configuration (parallel)

**Phase 5 - User Story 3**:
- T058-T061: Backend batch logic (sequential)
- T062-T065: ZIP endpoint (parallel with T058-T061)
- T066-T069: Frontend batch UI (parallel with backend)
- T070-T073: Frontend logic (sequential, after UI)

**Phase 6 - Polish** (Most can run in parallel):
- Documentation: T074-T076 (all parallel)
- Performance: T077-T079 (all parallel)
- Security: T080-T082 (all parallel)
- Deployment: T083-T089 (all parallel)
- Validation: T090-T093 (sequential)

---

## Parallel Example: Foundational Phase (Phase 2)

```bash
# Launch backend services foundation in parallel:
T020: Implement binary executor utility in web/backend/src/utils/binary_executor.py
T021: Implement file validators in web/backend/src/utils/validators.py

# Launch frontend core infrastructure in parallel:
T026: Create API client service in web/frontend/src/services/watermarkApi.ts
T027: Create TypeScript types in web/frontend/src/types/api.ts
```

## Parallel Example: User Story 1 - Models Phase

```bash
# Launch all models for User Story 1 together:
T028: Create Upload Session model in web/backend/src/api/models.py
T029: Create Processing Job model in web/backend/src/api/models.py
T030: Create Image Metadata model in web/backend/src/api/models.py

# Launch all frontend components for User Story 1 together:
T038: Create TurnstileWidget component in web/frontend/src/components/TurnstileWidget.tsx
T039: Create UploadZone component in web/frontend/src/components/UploadZone.tsx
T040: Create ProcessingIndicator component in web/frontend/src/components/ProcessingIndicator.tsx
T041: Create ImagePreview component in web/frontend/src/components/ImagePreview.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T027) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T028-T048)
4. **STOP and VALIDATE**: Test single image upload workflow end-to-end
5. Deploy MVP to dev environment, gather user feedback

**MVP Deliverable**: Users can upload a watermarked image via web browser, see processing indicator, and download cleaned result in < 5 seconds. No Turnstile yet (can add later), no batch processing (future enhancement).

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Binary compilation works, backend/frontend frameworks initialized
2. **MVP** (Phase 3: US1) → Single image upload functional → Test independently → Deploy to dev
3. **Bot Protection** (Phase 4: US2) → Turnstile verification enforced → Test independently → Deploy to dev
4. **Batch Processing** (Phase 5: US3) → Multi-image upload + ZIP download → Test independently → Deploy to dev
5. **Production Ready** (Phase 6: Polish) → Kubernetes deployment, performance optimizations, security hardening → Deploy to prod

Each phase adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done, parallelize**:
   - **Developer A**: User Story 1 backend (T028-T037)
   - **Developer B**: User Story 1 frontend (T038-T048)
   - **Developer C**: Deployment configs (T083-T088) and documentation (T074-T076)
3. **After US1 completes**:
   - **Developer A**: User Story 2 (T049-T057)
   - **Developer B**: User Story 3 (T058-T073)
   - **Developer C**: Polish tasks (T077-T082)
4. **Final validation**: All developers run quickstart.md validation (T090-T094)

---

## Task Summary

**Total Tasks**: 94

### Tasks by Phase:
- **Phase 1 (Setup)**: 8 tasks (T001-T008)
- **Phase 2 (Foundational)**: 19 tasks (T009-T027)
- **Phase 3 (User Story 1 - P1)**: 21 tasks (T028-T048)
- **Phase 4 (User Story 2 - P2)**: 9 tasks (T049-T057)
- **Phase 5 (User Story 3 - P3)**: 16 tasks (T058-T073)
- **Phase 6 (Polish)**: 21 tasks (T074-T094)

### Tasks by User Story:
- **Shared Infrastructure**: 27 tasks (Setup + Foundational)
- **User Story 1 (Single Image)**: 21 tasks
- **User Story 2 (Turnstile)**: 9 tasks
- **User Story 3 (Batch Processing)**: 16 tasks
- **Cross-Cutting (Polish)**: 21 tasks

### Parallel Opportunities:
- **Setup**: 5 of 8 tasks can run in parallel
- **Foundational**: 7 of 19 tasks can run in parallel
- **User Story 1**: 10 of 21 tasks can run in parallel
- **User Story 2**: 5 of 9 tasks can run in parallel
- **User Story 3**: 7 of 16 tasks can run in parallel
- **Polish**: 14 of 20 tasks can run in parallel

**Total Parallelizable Tasks**: 48 of 93 (52% can run concurrently with proper task distribution)

---

## Notes

- **[P] marker**: Indicates tasks that can run in parallel (different files, no blocking dependencies)
- **[Story] label**: Maps task to specific user story (US1, US2, US3) for traceability and independent testing
- **Tests NOT included**: Feature specification does not explicitly request TDD approach, so no test tasks generated
- **MVP recommendation**: Complete through User Story 1 (T001-T048) for initial launch, then iterate with US2 and US3
- **Commit strategy**: Commit after each task or logical group (e.g., all models for a story)
- **Validation checkpoints**: Stop after each user story phase to test independently before proceeding
- **File conflicts**: Avoid parallel edits to same file (e.g., T033-T037 modify same routes.py, must be sequential)
- **Constitution compliance**: T093 verifies all 7 constitutional principles are satisfied

**Ready to implement!** Start with Phase 1 (Setup), then Phase 2 (Foundational), then User Story 1 (MVP).
