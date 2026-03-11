# Image Building

The Image Building workflow orchestrates container image creation for the Omnia platform components.

## What It Does

The Image Building workflow provides:
- Container image build orchestration
- Multi-architecture image support (x86_64, aarch64)
- Docker and Podman integration
- Build context management and optimization
- Image security scanning and validation
- Registry push and distribution management

## Inputs/Outputs

**Inputs:**
- Build specifications and Dockerfiles
- Package lists from local repositories
- Build parameters and configurations
- Security scanning requirements

**Outputs:**
- Built container images
- Image metadata and manifests
- Security scan reports
- Registry push confirmations
- Build logs and artifacts

## Key Logic Locations

**Primary Files:**
- `api/build_image/routes.py` - HTTP endpoints for build operations
- `orchestrator/build_image/use_cases/` - Build orchestration logic
- `core/build_image/entities.py` - Build domain entities
- `core/build_image/repositories.py` - Build data access
- `core/build_image/services.py` - Build management services

**Main Components:**
- **BuildImageUseCase** - Orchestrates image build processes
- **BuildService** - Manages build execution and monitoring
- **MultiArchBuilder** - Handles multi-architecture builds
- **SecurityScanner** - Performs image security analysis

## Workflow Flow

1. **Build Request**: Client submits image build request
2. **Build Context Preparation**: Dockerfiles and dependencies assembled
3. **Multi-Arch Setup**: Build configurations prepared for target architectures
4. **Build Execution**: Container images built using Docker/Podman
5. **Security Scanning**: Built images scanned for vulnerabilities
6. **Manifest Creation**: Multi-architecture manifests generated
7. **Registry Push**: Images pushed to container registries
8. **Validation**: Final image validation and testing

## Architecture Support

Supports multiple CPU architectures:
- **x86_64** - Standard 64-bit Intel/AMD processors
- **aarch64** - 64-bit ARM processors
- **Multi-arch manifests** - Single image supporting multiple architectures

## Build Optimization

Optimizations include:
- **Layer caching** - Reusing unchanged layers across builds
- **Parallel builds** - Concurrent building for multiple architectures
- **Context optimization** - Minimizing build context size
- **Dependency caching** - Caching package downloads

## Security Features

Security capabilities include:
- **Vulnerability scanning** - Automated security analysis
- **Base image validation** - Verified base image sources
- **Signature verification** - Package integrity checks
- **Runtime security** - Secure container configurations

## Integration Points

- Receives packages from local repository workflow
- Integrates with validation workflow for quality checks
- Uses Vault for registry credentials
- Connects to container registries for distribution

## Configuration

Build configuration includes:
- Build parameters and environment variables
- Registry endpoints and credentials
- Security scanning policies
- Architecture-specific settings

## Error Handling

- Detailed build error reporting
- Step-by-step build progress tracking
- Rollback capabilities for failed builds
- Automated retry for transient failures

## Monitoring

- Real-time build progress monitoring
- Resource usage tracking (CPU, memory, storage)
- Build success/failure metrics
- Security scan result tracking

## Registry Integration

Supports multiple container registries:
- **Docker Hub** - Public container registry
- **Harbor** - Enterprise container registry
- **Artifactory** - JFrog container registry
- **Custom registries** - Organization-specific registries
