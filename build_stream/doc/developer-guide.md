# Build Stream Developer Guide

This guide provides developers with comprehensive documentation for understanding and working with the Build Stream codebase.

## Quick Start

**For New Developers:**
1. Read the main [README](../README.md) for architecture overview
2. Review this guide for end-to-end workflow understanding
3. Explore specific workflow documentation for detailed implementation
4. Set up development environment using the instructions below

**Key Concepts:**
- **Jobs**: Orchestrate multi-stage build processes
- **Stages**: Individual workflow steps (catalog, repo, build, validate)
- **Artifacts**: Generated files and outputs from workflows
- **Audit Trail**: Complete logging of all operations

## Architecture Deep Dive

### Layer Structure

```
build_stream/
├── api/           # HTTP layer - FastAPI routes and middleware
├── core/          # Domain layer - Business logic and entities
├── orchestrator/  # Application layer - Use cases and workflow coordination
├── infra/         # Infrastructure layer - External integrations
├── common/        # Shared layer - Utilities and configuration
└── doc/           # Documentation layer - Workflow guides
```

### Dependency Flow

```
HTTP Request → API Routes → Use Cases → Core Services → Repositories
                    ↓              ↓              ↓
               Authentication   Business Logic  Data Persistence
                    ↓              ↓              ↓
               Authorization   Validation      External Systems
```

## Workflow Tracing Guide

### End-to-End Job Flow

To trace a complete job from start to finish:

1. **Job Creation** (`POST /api/v1/jobs`)
   - Entry point: `api/jobs/routes.py`
   - Use case: `orchestrator/jobs/use_cases/create_job.py`
   - Entity: `core/jobs/entities.py`

2. **Stage Processing** (Async)
   - Each stage runs independently
   - Result polling handles completion
   - Status updates tracked in database

3. **Artifact Storage**
   - Files stored in configured artifact store
   - Metadata tracked in database
   - Access controlled through permissions

### Debugging Workflow Issues

**Common Debugging Steps:**
1. Check job status via `/api/v1/jobs/{job_id}`
2. Review stage-specific error messages
3. Examine audit trail for detailed execution logs
4. Validate inputs using validation workflow
5. Check external system connectivity (Vault, repositories, registries)

**Key Debug Files:**
- `api/logging_utils.py` - Centralized logging configuration
- `core/exceptions.py` - Domain-specific error definitions
- `infra/` - External integration points

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd build_stream

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.test .env
# Edit .env with your configuration

# Run database migrations (if using SQL backend)
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Features

**1. Add New API Endpoint:**
- Create route in appropriate `api/` subdirectory
- Add schema definitions for request/response
- Implement authentication/authorization as needed
- Add to `api/router.py` for registration

**2. Add New Business Logic:**
- Create entities in `core/` domain
- Implement repositories for data access
- Create use cases in `orchestrator/`
- Wire up in dependency injection container

**3. Add New Workflow Stage:**
- Define stage type in `core/jobs/value_objects.py`
- Implement stage-specific logic
- Add to job creation workflow
- Update documentation

### Testing Strategy

**Unit Tests:**
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic validation

**Integration Tests:**
- Test workflow end-to-end
- Use test database and artifact store
- Validate cross-component interactions

**API Tests:**
- Test HTTP endpoints thoroughly
- Validate authentication and authorization
- Test error scenarios and edge cases

## Common Patterns

### Dependency Injection

Build Stream uses `dependency-injector` for IoC:

```python
# In container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Repository providers
    job_repository = providers.Singleton(
        SqlJobRepository,
        session_factory=SessionLocal,
    )
    
    # Use case providers
    create_job_use_case = providers.Factory(
        CreateJobUseCase,
        job_repository=job_repository,
        # ... other dependencies
    )
```

### Error Handling

Consistent error handling across all layers:

```python
# Domain exceptions
class JobNotFoundError(Exception):
    """Raised when a job is not found."""

# API error handling
@app.exception_handler(JobNotFoundError)
async def job_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Job not found", "details": str(exc)}
    )
```

### Logging

Structured logging with correlation IDs:

```python
from api.logging_utils import log_secure_info

log_secure_info(
    "Job created successfully",
    extra={
        "job_id": str(job_id),
        "client_id": str(client_id),
        "stages": [stage.name for stage in stages]
    }
)
```

## Security Considerations

### Authentication Flow

1. Client authenticates with JWT token
2. Token validated in middleware
3. User context attached to request
4. Authorization checked per endpoint

### Secure Data Handling

- Never log sensitive data (passwords, tokens)
- Use Vault for credential storage
- Implement proper access controls
- Audit all sensitive operations

### Input Validation

All inputs validated using:
- Pydantic models for type checking
- JSON schemas for structure validation
- Business rules in domain layer
- Security scanning for malicious content

## Performance Optimization

### Database Optimization

- Use connection pooling
- Implement proper indexing
- Batch operations where possible
- Monitor query performance

### Async Processing

- Use async/await for I/O operations
- Implement proper error handling
- Monitor async task completion
- Handle resource cleanup

### Caching Strategies

- Cache frequently accessed data
- Use appropriate cache invalidation
- Monitor cache hit rates
- Consider distributed caching for scale

## Troubleshooting Common Issues

### Job Failures

**Symptoms:** Jobs stuck in running state or failing unexpectedly

**Debug Steps:**
1. Check job status and stage details
2. Review error messages in audit trail
3. Verify external system connectivity
4. Check resource availability

### Performance Issues

**Symptoms:** Slow API responses or job processing

**Debug Steps:**
1. Monitor database query performance
2. Check resource utilization
3. Review async task processing
4. Analyze network connectivity

### Authentication Problems

**Symptoms:** 401/403 errors on API calls

**Debug Steps:**
1. Verify JWT token validity
2. Check user permissions
3. Review token expiration
4. Validate token claims

## External Dependencies

### Required Services

- **PostgreSQL** - Primary data storage
- **Vault** - Secure credential storage
- **Pulp** - Repository management (optional)
- **Container Registry** - Image storage

### Optional Integrations

- **External CI/CD** - Build pipeline integration
- **Monitoring Systems** - Metrics and alerting
- **Security Scanners** - Vulnerability assessment
- **Compliance Tools** - Regulatory reporting

## Contributing Guidelines

### Code Standards

- Follow PEP 8 for Python code
- Use type hints for all public functions
- Write comprehensive docstrings
- Include unit tests for new features

### Documentation Requirements

- Update README for API changes
- Document new workflows in `doc/`
- Update architecture diagrams
- Include examples in docstrings

### Review Process

1. Create feature branch from main
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. Address review feedback
6. Merge after approval
