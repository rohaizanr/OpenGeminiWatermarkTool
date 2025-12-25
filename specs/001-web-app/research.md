# Research: Web Application for Watermark Removal

**Feature**: 001-web-app  
**Date**: 2025-12-25  
**Purpose**: Document technology choices, best practices, and architectural decisions for web application implementation

## Research Overview

This document resolves all "NEEDS CLARIFICATION" items from Technical Context and provides rationale for key technology selections. Research covers frontend framework selection, backend API design, containerization strategy, Material Design 3 implementation, and deployment architecture.

---

## 1. Frontend Framework: Next.js vs Alternatives

**Decision**: Next.js 14+ with App Router

**Rationale**:
- **SEO Requirement**: Specification explicitly requires SSR for search engine optimization. Next.js provides built-in SSR and static site generation (SSG) without additional configuration
- **React Ecosystem**: Material Design 3 has robust React component libraries (Material Web Components can be wrapped in React)
- **Performance**: Automatic code splitting, image optimization, and edge caching align with Core Web Vitals targets (LCP < 2.5s)
- **Developer Experience**: TypeScript support, hot module replacement, and file-based routing accelerate development
- **Cloudflare Deployment**: Next.js has first-class support for Cloudflare Pages via `@cloudflare/next-on-pages` adapter

**Alternatives Considered**:
- **Vite + React SPA**: Rejected because SSR for SEO would require custom server setup, losing simplicity
- **Remix**: Strong SSR support but smaller ecosystem for Material 3 components and less Cloudflare Pages documentation
- **SvelteKit**: Excellent performance but smaller community for Material Design 3 integrations

**Best Practices**:
- Use App Router (not Pages Router) for nested layouts and streaming SSR
- Implement route-based code splitting to minimize initial bundle size
- Use `next/image` for automatic image optimization
- Configure ISR (Incremental Static Regeneration) for static content pages
- Deploy static exports to Cloudflare Pages for global edge distribution

**References**:
- Next.js 14 App Router documentation: https://nextjs.org/docs/app
- Cloudflare Pages Next.js guide: https://developers.cloudflare.com/pages/framework-guides/nextjs/

---

## 2. Material Design 3 Implementation

**Decision**: Material Web Components + React wrappers + Tailwind CSS for utilities

**Rationale**:
- **Official Components**: Google's Material Web Components are the canonical implementation of Material 3 design system
- **React Compatibility**: Components can be wrapped using React's Web Component support or third-party wrappers (e.g., `@material/web-react`)
- **Tailwind Integration**: Use Tailwind for spacing, layout utilities while Material Web handles themed UI components (buttons, cards, progress indicators)
- **Material You Theming**: Built-in dynamic color theming and elevation system per Material 3 spec
- **Accessibility**: Components follow WCAG 2.1 AA standards out of the box

**Alternatives Considered**:
- **MUI (Material-UI) v6**: Does not yet fully implement Material Design 3 (as of 2025-12-25); still based on Material 2
- **Custom CSS Implementation**: Rejected due to high maintenance burden and risk of design inconsistencies
- **Vuetify/Angular Material**: Framework lock-in incompatible with Next.js/React choice

**Best Practices**:
- Define Material You color tokens in CSS variables for global theming
- Use semantic component names (e.g., `<md-filled-button>` not generic `<Button>`)
- Implement dark mode support via `prefers-color-scheme` media query
- Test components with screen readers for accessibility compliance
- Use Material 3 elevation tokens (0-5) for consistent depth hierarchy

**References**:
- Material Design 3 guidelines: https://m3.material.io/
- Material Web Components: https://github.com/material-components/material-web
- React integration guide: https://material-web.dev/frameworks/react/

---

## 3. Backend Framework: FastAPI vs Alternatives

**Decision**: FastAPI 0.104+ with Uvicorn ASGI server

**Rationale**:
- **Performance**: ASGI-based async framework handles concurrent image uploads efficiently (target: 100 concurrent users)
- **Type Safety**: Pydantic models provide automatic request/response validation with TypeScript-like type hints
- **OpenAPI Generation**: Automatic OpenAPI 3.0 spec generation for contract testing and frontend API client generation
- **Python Ecosystem**: Pillow for image validation, httpx for Turnstile verification, slowapi for rate limiting integrate seamlessly
- **Binary Execution**: Python's `subprocess` module provides clean interface for invoking compiled C++ GeminiWatermarkTool binary

**Alternatives Considered**:
- **Flask**: Synchronous nature would struggle with concurrent file uploads; lacks modern async support
- **Django**: Overpowered for stateless API (no need for ORM, admin panel, template engine)
- **Go (Gin/Fiber)**: Excellent performance but smaller ecosystem for image processing libraries; Python interop with existing tools more natural
- **Rust (Axum)**: Maximum performance but steeper learning curve and longer development time for MVP

**Best Practices**:
- Use dependency injection for config, logging, and external services (Turnstile)
- Implement background tasks with `BackgroundTasks` for file cleanup
- Use middleware for CORS, rate limiting, and request logging
- Structure code with repository pattern (services/ directory) for testability
- Expose `/health` and `/readiness` endpoints for Kubernetes probes

**References**:
- FastAPI documentation: https://fastapi.tiangolo.com/
- Python subprocess for binary execution: https://docs.python.org/3/library/subprocess.html
- slowapi rate limiting: https://github.com/laurents/slowapi

---

## 4. Container Strategy: Multi-Stage Builds

**Decision**: Three-stage Docker build process

**Stage 1 - Builder Container** (`build/Dockerfile.builder`):
- Base: `ubuntu:22.04` (glibc 2.35+ for compatibility)
- Install: CMake 3.21+, vcpkg, GCC 10+, Ninja
- Build: Compile GeminiWatermarkTool binary with static linking
- Output: Single statically-linked binary (`/build/GeminiWatermarkTool`)

**Stage 2 - Python API Container** (`backend/Dockerfile`):
- Base: `python:3.11-alpine` (minimal size)
- Copy: Compiled binary from builder stage
- Install: Python dependencies (FastAPI, Uvicorn, Pillow, etc.)
- Expose: Port 8000
- Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

**Stage 3 - Frontend Build** (handled by Cloudflare Pages):
- Next.js static export or edge runtime
- Deploy to Cloudflare global network

**Rationale**:
- **Size Optimization**: Alpine-based Python image (~50MB base) vs Ubuntu (~200MB); final backend image < 200MB
- **Security**: Minimal attack surface with Alpine; no unnecessary build tools in runtime container
- **Separation of Concerns**: Build complexity isolated in builder stage; runtime container only has execution requirements
- **CI/CD Efficiency**: Builder stage cached separately; Python dependencies cached in their own layer

**Best Practices**:
- Use `.dockerignore` to exclude node_modules, __pycache__, test files
- Pin base image versions for reproducibility (`python:3.11.7-alpine`)
- Run containers as non-root user for security
- Use health checks in Dockerfile (`HEALTHCHECK CMD curl --fail http://localhost:8000/health`)
- Leverage BuildKit for parallel multi-stage builds

**References**:
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Alpine Linux advantages: https://alpinelinux.org/about/

---

## 5. Cloudflare Turnstile Integration

**Decision**: Cloudflare Turnstile with "Managed" challenge mode

**Rationale**:
- **Zero Friction**: "Managed" mode shows challenges only for suspicious traffic; legitimate users pass invisibly
- **Privacy**: No user tracking or data collection (vs reCAPTCHA)
- **Performance**: Lightweight widget (~10KB) vs reCAPTCHA (~300KB)
- **Integration**: Simple JavaScript widget + backend token verification via Cloudflare API

**Implementation Approach**:
- **Frontend**: Embed Turnstile widget in upload zone; obtain token on successful challenge
- **Backend**: Validate token via POST to `https://challenges.cloudflare.com/turnstile/v0/siteverify` before processing upload
- **Token Lifecycle**: 5-minute expiration; frontend re-challenges on timeout

**Best Practices**:
- Store site key in environment variables (public, but scoped to domain)
- Store secret key in GCP Secret Manager (backend verification)
- Implement retry logic for Turnstile API verification failures
- Show user-friendly message if challenge fails ("Please complete verification")
- Monitor verification success rates in logs

**References**:
- Cloudflare Turnstile docs: https://developers.cloudflare.com/turnstile/
- React integration: https://github.com/marsidev/react-turnstile

---

## 6. Deployment Architecture

### Development Environment

**Decision**: Docker Compose with hot-reload

**Services**:
```yaml
services:
  backend:
    build: ./backend
    volumes:
      - ./backend/src:/app/src  # Hot reload
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - TURNSTILE_SECRET=test_secret
      
  frontend:
    build: ./frontend
    volumes:
      - ./frontend/src:/app/src  # Hot reload
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Best Practices**:
- Use `docker-compose.override.yml` for developer-specific settings
- Mount source code for hot-reload during development
- Use environment-specific `.env` files (`.env.development`, `.env.production`)

### Production Environment

**Backend - Google Kubernetes Engine (GKE)**:

**Decision**: GKE Autopilot mode with Horizontal Pod Autoscaler

**Configuration**:
- **Cluster**: GKE Autopilot (managed node pools, auto-scaling, auto-upgrade)
- **Deployment**: 2-10 replicas based on CPU (target: 70% utilization) and memory (target: 80%)
- **Resource Limits**: 2 CPU cores, 2GB RAM per pod
- **Storage**: emptyDir volumes (ephemeral, pod-local)
- **Ingress**: GKE Ingress with HTTPS (Google-managed SSL certificates)
- **Secrets**: GCP Secret Manager integration via Workload Identity
- **Monitoring**: Cloud Logging and Cloud Monitoring (Prometheus-compatible)

**Rationale**:
- **Autopilot**: Reduces operational overhead (no node management, automatic patching)
- **Auto-scaling**: Handles traffic spikes gracefully (100+ concurrent users)
- **Workload Identity**: Secure access to GCP services without service account keys

**Frontend - Cloudflare Pages**:

**Decision**: Cloudflare Pages with edge caching

**Configuration**:
- **Build Command**: `npm run build` (Next.js static export or edge runtime)
- **Output Directory**: `out/` or `.vercel/output/`
- **Environment Variables**: API_URL, TURNSTILE_SITE_KEY
- **Edge Caching**: Automatic for static assets; API routes proxied to backend
- **Domains**: Custom domain with automatic SSL

**Rationale**:
- **Global Distribution**: 200+ edge locations for low-latency delivery
- **Zero Config**: GitHub integration for automatic deployments on push
- **Cost**: Free tier supports millions of requests per month
- **DDoS Protection**: Built-in Cloudflare security features

**Best Practices**:
- Use Terraform or kubectl for GKE infrastructure as code
- Implement rolling updates with readiness probes (`initialDelaySeconds: 10`)
- Configure liveness probes to restart unhealthy pods
- Use Cloudflare Workers for advanced edge logic (optional future enhancement)
- Set up alerts for pod restarts, high CPU/memory, API error rates

**References**:
- GKE Autopilot: https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview
- Cloudflare Pages: https://developers.cloudflare.com/pages/

---

## 7. Rate Limiting Strategy

**Decision**: Token bucket algorithm via slowapi + Redis (optional for distributed systems)

**Implementation**:
- **Library**: slowapi (FastAPI extension for rate limiting)
- **Strategy**: 10 requests per minute per IP address
- **Storage**: In-memory (development), Redis (production for multi-pod consistency)
- **Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

**Best Practices**:
- Return HTTP 429 (Too Many Requests) with `Retry-After` header
- Whitelist trusted IPs (e.g., monitoring services) if needed
- Log rate limit violations for abuse detection
- Consider user-based rate limiting (via session tokens) for authenticated features (future)

**References**:
- slowapi documentation: https://github.com/laurents/slowapi

---

## 8. Image Processing Workflow

**Decision**: Synchronous processing with subprocess invocation

**Flow**:
1. Frontend uploads image with Turnstile token
2. Backend validates token, file format, and size
3. Backend saves file to ephemeral storage (`/tmp/uploads/{uuid}`)
4. Backend invokes GeminiWatermarkTool binary: `subprocess.run(['./GeminiWatermarkTool', '-i', input_path, '-o', output_path])`
5. Backend reads processed image, returns to frontend
6. Background task deletes input/output files after response sent

**Error Handling**:
- Binary exit code ≠ 0 → Return HTTP 500 with error message
- Timeout after 30 seconds → Return HTTP 504 (Gateway Timeout)
- Corrupted image → Binary detects and exits with error (caught by backend)

**Best Practices**:
- Use UUIDs for file names to prevent collisions
- Set subprocess timeout to prevent hanging processes
- Capture binary stderr for detailed error logging
- Implement exponential backoff for transient failures (optional)

---

## Summary of Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Frontend Framework** | Next.js 14+ (App Router) | SSR for SEO, React ecosystem, Cloudflare Pages support |
| **UI Library** | Material Web Components + Tailwind | Official Material 3 implementation, WCAG 2.1 AA compliant |
| **Backend Framework** | FastAPI 0.104+ | Async performance, type safety, OpenAPI generation |
| **Container Strategy** | Multi-stage Docker builds | Size optimization, security, CI/CD efficiency |
| **Bot Protection** | Cloudflare Turnstile | Privacy-focused, lightweight, Cloudflare-native |
| **Backend Deployment** | GKE Autopilot | Managed Kubernetes, auto-scaling, Workload Identity |
| **Frontend Deployment** | Cloudflare Pages | Global CDN, zero config, automatic HTTPS |
| **Rate Limiting** | slowapi + Redis | Token bucket algorithm, distributed consistency |
| **Image Processing** | Subprocess (Python → C++ binary) | Reuses existing tool, clean separation of concerns |

**All NEEDS CLARIFICATION items resolved.** Ready to proceed to Phase 1 (data-model.md, contracts/, quickstart.md).
