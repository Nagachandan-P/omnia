# Jobs Management

The Jobs workflow manages the complete lifecycle of build jobs in Build Stream, from creation through completion and monitoring.

## What It Does

The Jobs workflow provides:
- Job creation with idempotency guarantees
- Stage-based execution with state management
- Real-time job monitoring and status tracking
- Audit trail for all job operations
- Result polling and notification handling

## Inputs/Outputs

**Inputs:**
- Job creation requests with stage definitions
- Authentication tokens for security
- Optional job parameters and configuration

**Outputs:**
- Job IDs for tracking
- Stage execution results
- Audit events for compliance
- Error details and diagnostics

## Key Logic Locations

**Primary Files:**
- `api/jobs/routes.py` - HTTP endpoints for job operations
- `orchestrator/jobs/use_cases/create_job.py` - Job creation business logic
- `core/jobs/entities.py` - Job and Stage domain entities
- `core/jobs/repositories.py` - Data access layer
- `core/jobs/services.py` - Job-related domain services

**Main Components:**
- **CreateJobUseCase** - Handles job creation with validation
- **JobRepository** - Manages job persistence
- **StageRepository** - Manages stage state tracking
- **ResultPoller** - Handles async result collection

## Workflow Flow

1. **Job Creation**: Client submits job via `/api/v1/jobs` endpoint
2. **Validation**: Request validated for authentication and schema
3. **Idempotency Check**: Prevents duplicate job creation
4. **Stage Initialization**: Job broken into executable stages
5. **Async Execution**: Stages queued for background processing
6. **Status Updates**: Job status tracked through state transitions
7. **Result Collection**: Results polled and stored
8. **Audit Logging**: All operations logged for traceability

## Stage Types

Jobs support multiple stage types:
- **catalog_roles** - Software catalog processing
- **local_repo** - Local repository creation
- **build_image** - Container image building
- **validate** - Input/output validation

## Error Handling

- Invalid state transitions are rejected
- Failed stages can be retried based on configuration
- Comprehensive error reporting with context
- Audit trail captures all error events

## Monitoring

- Job status available via `/api/v1/jobs/{job_id}` endpoint
- List all jobs with filtering options
- Real-time status updates through result polling
- Detailed audit trail for compliance reporting

## Integration Points

- Integrates with all other workflows as stages
- Uses Vault for secure credential access
- Stores artifacts in configured artifact store
- Emits events for external system integration
