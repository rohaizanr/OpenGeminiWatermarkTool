<!--
╔════════════════════════════════════════════════════════════════════════════╗
║ SYNC IMPACT REPORT - Constitution v1.0.0                                  ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Version Change: INITIAL → 1.0.0                                            ║
║ Type: MINOR (Initial constitution establishment)                           ║
║                                                                             ║
║ Created Principles:                                                         ║
║   • I. Cross-Platform Performance & Determinism                             ║
║   • II. Mathematical Correctness & Precision                                ║
║   • III. User Experience & Accessibility                                    ║
║   • IV. Material Design 3 UI Standards                                      ║
║   • V. Dual Environment Architecture                                        ║
║   • VI. Zero Dependencies Philosophy                                        ║
║   • VII. Security & Data Safety                                             ║
║                                                                             ║
║ Added Sections:                                                             ║
║   • Technology Stack & Architecture                                         ║
║   • Development & Deployment Workflow                                       ║
║   • Governance                                                              ║
║                                                                             ║
║ Templates Requiring Updates:                                                ║
║   ✅ plan-template.md (Constitution Check section aligned)                 ║
║   ✅ spec-template.md (User Scenarios structure compatible)                ║
║   ✅ tasks-template.md (Phase categorization matches principles)           ║
║   ⚠️  RECOMMENDED: Add Material 3 design checkpoints to checklist          ║
║   ⚠️  RECOMMENDED: Add environment-specific deployment validation          ║
║                                                                             ║
║ Follow-up TODOs:                                                            ║
║   • Add Material 3 design compliance checklist items                        ║
║   • Document Kubernetes deployment configuration                            ║
║   • Document Cloudflare deployment configuration                            ║
║   • Create environment-specific testing guidelines                          ║
╚════════════════════════════════════════════════════════════════════════════╝
-->

# GeminiWatermarkTool Constitution

## Core Principles

### I. Cross-Platform Performance & Determinism

**Watermark removal MUST be mathematically accurate and deterministic across all platforms.**

This tool performs reverse alpha blending to restore original pixels without guessing or AI inpainting. Every implementation MUST:
- Use the same mathematical algorithm producing identical output on Windows, Linux, macOS, and Android
- Maintain single executable deployment with zero runtime dependencies
- Support in-place editing, explicit input/output, and batch directory processing
- Auto-detect watermark size (48×48 vs 96×96) without user configuration
- Process images offline without network requirements

**Rationale**: Users depend on consistent results. Determinism ensures reproducibility for workflows involving slides, documents, UI screenshots, diagrams, and logos where precision matters.

### II. Mathematical Correctness & Precision

**Pixel restoration MUST use precise reverse alpha blending equations—no approximations.**

The core algorithm MUST:
- Implement exact mathematical inversion of alpha blending operations
- Preserve pixel-perfect accuracy for text-heavy content (slides, documents)
- Avoid generative/AI-based inpainting that warps edges, spacing, or strokes
- Handle edge cases in watermark detection gracefully with clear error messages
- Validate input images and watermark regions before processing

**Rationale**: Text and diagram clarity cannot be compromised. Mathematical accuracy prevents the visual artifacts common in ML-based inpainting approaches.

### III. User Experience & Accessibility

**The tool MUST be accessible to non-technical users while supporting advanced workflows.**

UX requirements:
- Simple drag-and-drop execution (Windows: drag image onto executable)
- Clear command-line interface with intuitive arguments
- Informative error messages guiding users to resolution
- Batch processing for multiple images or directories
- Optional verbose logging for troubleshooting
- Clear warnings about in-place file overwriting with backup recommendations

**Rationale**: Barrier-free adoption ensures broad utility. Users range from casual consumers to professional content creators needing batch automation.

### IV. Material Design 3 UI Standards

**Web interface MUST strictly follow Google Material Design 3 guidelines for layout, components, and interactions.**

UI implementation requirements:
- Adopt Material You color theming with dynamic color support
- Use Material 3 component library (buttons, cards, dialogs, progress indicators)
- Implement three-step workflow layout inspired by LastSnap reference:
  1. Upload area (drag-and-drop with file picker fallback)
  2. Processing indicator (auto-extraction feedback)
  3. Download/preview result (image preview with save/drag options)
- Ensure accessibility compliance (WCAG 2.1 AA minimum)
- Support responsive layouts (mobile, tablet, desktop)
- Implement elevation, motion, and typography per Material 3 specs

**Rationale**: Consistent Material Design 3 adherence ensures familiar, accessible, and polished web experience aligned with modern Google ecosystem standards.

### V. Dual Environment Architecture

**Development and production environments MUST be isolated with environment-specific configurations.**

Environment architecture:
- **Development Environment**:
  - Local testing with hot-reload support
  - Mock/stub external services for offline development
  - Comprehensive logging enabled by default
  - Database seeding for consistent test data
  
- **Production Environment**:
  - **Backend**: Deployed on Google Cloud Platform using Kubernetes (GKE)
    - Auto-scaling pods based on load
    - Health checks and readiness probes
    - Secrets management via GCP Secret Manager
    - Structured logging to Cloud Logging
  - **Frontend**: Deployed to Cloudflare Pages/Workers
    - Edge caching for static assets
    - Global CDN distribution
    - Automatic HTTPS and DDoS protection
    - Environment variables via Cloudflare dashboard

**Configuration Management**:
- Environment-specific config files (dev.env, prod.env)
- No secrets in version control
- CI/CD pipelines verify environment isolation

**Rationale**: Environment isolation prevents configuration leaks, ensures reproducible builds, and optimizes deployment for cloud-native infrastructure.

### VI. Zero Dependencies Philosophy

**CLI executable MUST remain standalone with no runtime dependencies.**

Dependency constraints:
- Single-file executable per platform
- Statically link all required libraries (OpenCV, fmt, CLI11, spdlog)
- Embed required assets at compile time
- No separate installer or package manager requirements
- Binary size optimized but never at the cost of removing core functionality

**Web/API Dependencies** (separate from CLI):
- Frontend: Modern framework (React/Vue/Svelte) with Material 3 component library
- Backend: Lightweight runtime (Go/Rust/Node.js) containerized for Kubernetes
- All web dependencies pinned with lock files for reproducibility

**Rationale**: Deployment friction kills adoption. A single executable ensures users can run the tool immediately after download without debugging missing libraries or system configurations.

### VII. Security & Data Safety

**User data MUST be protected, and file operations MUST be reversible when possible.**

Security requirements:
- **Local CLI Tool**:
  - No telemetry or network requests
  - No file access beyond explicitly provided paths
  - Clear warnings before destructive operations (in-place edits)
  - Validate image formats to prevent malformed input exploits
  
- **Web Application**:
  - Process images server-side (never store originals long-term)
  - Delete uploaded files after processing (configurable retention: 1 hour max)
  - Rate limiting to prevent abuse
  - Input sanitization for all API endpoints
  - HTTPS-only communication
  - CORS policies restricting origins

**Backup Policy**:
- Recommend users back up originals before in-place edits
- Provide explicit output path option to preserve originals
- Display prominent disclaimer about data loss risks in documentation

**Rationale**: User trust depends on transparent data handling. Security-first design prevents misuse while respecting privacy.

## Technology Stack & Architecture

### Core CLI Technology
- **Language**: C++ (C++17 minimum for cross-platform compatibility)
- **Build System**: CMake with vcpkg dependency management
- **Primary Libraries**:
  - OpenCV 4 (JPEG, PNG, WebP support only—no full build)
  - fmt (string formatting)
  - CLI11 (command-line parsing)
  - spdlog (structured logging)
- **Platforms**: Windows (x64), Linux (x64), macOS (Universal—Intel + Apple Silicon), Android (ARM64)

### Web Application Technology
- **Frontend Framework**: React/Vue/Svelte with Material 3 (Material Web Components)
- **State Management**: Context API / Vuex / Svelte Stores (framework-specific)
- **Build Tool**: Vite (fast builds, HMR support)
- **Deployment**: Cloudflare Pages with edge caching

### Backend/API Technology
- **Language**: Go / Rust / Node.js (choose based on team expertise)
- **Container Runtime**: Docker with multi-stage builds
- **Orchestration**: Google Kubernetes Engine (GKE)
- **API Framework**:
  - Go: Gin / Fiber
  - Rust: Axum / Actix-web
  - Node.js: Fastify / Express
- **Storage**: Cloud Storage (temporary file processing only)
- **Monitoring**: Google Cloud Monitoring + Logging

### CI/CD
- **Version Control**: Git with GitHub
- **CI Pipeline**: GitHub Actions
  - Automated builds for all platforms
  - Unit and integration tests
  - Security scanning (Dependabot, CodeQL)
  - Docker image builds and pushes to GCP Artifact Registry
- **CD Pipeline**:
  - Frontend: Automatic deployment to Cloudflare on main branch push
  - Backend: GitOps with ArgoCD or kubectl apply to GKE

## Development & Deployment Workflow

### Development Phase
1. **Feature Specification**: Follow spec-template.md with prioritized user stories
2. **Implementation Planning**: Use plan-template.md to document architecture
3. **Task Breakdown**: Generate tasks.md with independent, testable increments
4. **Code Review**: All changes require peer review before merge
5. **Testing**: Comprehensive tests (unit, integration, contract) per constitution principles

### Local Development
- Use Docker Compose for backend services
- Run frontend dev server with hot reload
- Mock external APIs for offline development
- Seed database with test data

### Deployment
- **Development Environment**:
  - Trigger: Push to develop branch
  - Deploy to: GKE development cluster + Cloudflare preview environment
  - Testing: Automated smoke tests + manual QA
  
- **Production Environment**:
  - Trigger: Tag release (vX.Y.Z) or push to main
  - Deploy to: GKE production cluster + Cloudflare production domain
  - Gates: All tests pass + manual approval
  - Rollback: Kubernetes rollout undo + Cloudflare instant rollback

## Governance

### Constitution Authority
This constitution supersedes all other development practices, guidelines, and conventions. Any conflict between this document and other project documentation MUST be resolved in favor of the constitution.

### Amendment Process
1. Propose amendment with rationale in GitHub issue
2. Document impact on existing code and workflows
3. Require approval from project maintainers
4. Update constitution version per semantic versioning rules:
   - **MAJOR**: Backward-incompatible governance changes or principle removals
   - **MINOR**: New principles added or sections materially expanded
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
5. Create migration plan for affected code/docs
6. Update `LAST_AMENDED_DATE` to amendment date

### Compliance Review
- All pull requests MUST verify constitution compliance before merge
- Architecture decisions requiring complexity beyond principles MUST justify deviations
- Quarterly audits ensure ongoing alignment

### Runtime Guidance
Use `.specify/templates/agent-file-template.md` for runtime development guidance that interprets these principles for AI coding agents.

**Version**: 1.0.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-25
