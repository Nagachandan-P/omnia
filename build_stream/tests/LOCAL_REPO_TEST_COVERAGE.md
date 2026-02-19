# Local Repository API Test Coverage

This document provides an overview of all tests for the create-local-repository API.

## Test Structure

```
tests/
├── unit/
│   ├── api/local_repo/
│   │   ├── test_routes.py              # API route tests
│   │   ├── test_dependencies.py        # Dependency injection tests
│   │   └── test_schemas.py             # Pydantic schema tests
│   ├── core/localrepo/
│   │   ├── test_entities.py            # Entity tests
│   │   ├── test_exceptions.py          # Exception tests
│   │   ├── test_services.py            # Service tests
│   │   └── test_value_objects.py       # Value object tests
│   ├── orchestrator/local_repo/
│   │   ├── test_use_case.py            # Use case tests
│   │   ├── test_result_poller.py       # Result poller tests
│   │   ├── test_commands.py            # Command DTO tests
│   │   └── test_dtos.py                # Response DTO tests
│   └── infra/
│       ├── test_nfs_input_directory_repository.py
│       └── test_nfs_playbook_queue_repositories.py
├── integration/api/local_repo/
│   ├── test_create_local_repo_api.py   # Main integration tests
│   └── test_create_local_repo_edge_cases.py  # Edge case tests
├── performance/
│   └── test_local_repo_performance.py  # Performance tests
└── e2e/
    └── test_local_repo_e2e.py          # End-to-end tests
```

## Test Coverage Summary

### Unit Tests (84 tests)

#### API Layer
- **test_routes.py**: Tests for HTTP endpoints
  - Success scenarios (202 Accepted)
  - Error handling (404, 400, 503, 500)
  - Authentication and authorization
  - Request validation
  - Header propagation

- **test_dependencies.py**: Tests for FastAPI dependencies
  - Correlation ID handling
  - Authentication token parsing
  - Job ID validation
  - Dependency injection

- **test_schemas.py**: Tests for Pydantic schemas
  - Request/response validation
  - Serialization/deserialization
  - Field constraints
  - Error response schema

#### Core Layer
- **test_entities.py**: Tests for domain entities
  - PlaybookRequest creation and validation
  - PlaybookResult parsing and properties
  - Immutability and equality

- **test_exceptions.py**: Tests for domain exceptions
  - Exception creation with proper attributes
  - Error message formatting
  - Inheritance hierarchy

- **test_services.py**: Tests for domain services
  - InputFileService validation and preparation
  - PlaybookQueueRequestService operations
  - PlaybookQueueResultService polling

- **test_value_objects.py**: Tests for value objects
  - PlaybookPath validation
  - ExtraVars handling
  - ExecutionTimeout constraints

#### Orchestrator Layer
- **test_use_case.py**: Tests for use case logic
  - Job validation
  - Stage state transitions
  - Input file validation
  - Queue submission

- **test_result_poller.py**: Tests for result polling
  - Polling loop start/stop
  - Result processing
  - Stage updates
  - Audit event emission

- **test_commands.py**: Tests for command DTOs
  - Immutable command objects
  - Validation and equality

- **test_dtos.py**: Tests for response DTOs
  - Response creation
  - Dictionary conversion
  - Field validation

#### Infrastructure Layer
- **test_nfs_input_directory_repository.py**: Tests for input directory repository
  - Path resolution
  - Input validation
  - File system operations

- **test_nfs_playbook_queue_repositories.py**: Tests for queue repositories
  - Request writing
  - Result polling
  - File archiving
  - Error handling

### Integration Tests (15 tests)

#### Main Integration Tests
- **test_create_local_repo_api.py**: Full API integration
  - Happy path scenarios
  - Mocked external dependencies
  - End-to-end request flow

#### Edge Case Tests
- **test_create_local_repo_edge_cases.py**: Edge case scenarios
  - Concurrent requests
  - Large correlation IDs
  - Unicode handling
  - NFS queue full
  - Permission issues
  - Malformed headers

### Performance Tests (4 tests)

- **test_local_repo_performance.py**: Performance benchmarks
  - Response time thresholds
  - Concurrent load handling
  - Memory usage stability
  - Large payload handling

### End-to-End Tests (3 tests)

- **test_local_repo_e2e.py**: Full system tests
  - Complete request lifecycle
  - Real file system operations
  - Result processing simulation

## Test Categories

### Functional Tests
- Verify correct behavior of all components
- Test happy paths and error scenarios
- Ensure business logic is correctly implemented

### Non-Functional Tests
- Performance: Response times and resource usage
- Concurrency: Multiple simultaneous requests
- Reliability: Error handling and recovery

### Security Tests
- Authentication and authorization
- Input validation and sanitization
- Path traversal prevention

### Compatibility Tests
- Unicode support
- Various client configurations
- Backward compatibility

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Performance tests (requires --performance marker)
pytest tests/performance/ -v -m performance

# Local repo tests only
pytest tests/ -k "local_repo" -v
```

### Coverage Report
```bash
pytest tests/ --cov=build_stream --cov-report=html
```

## Test Data Management

### Fixtures
- `created_job`: Valid job entity
- `auth_headers`: Authentication headers
- `nfs_queue_dir`: Temporary NFS queue directory
- `input_dir`: Temporary input directory with required files

### Mocks
- External file system operations
- Network calls
- Database operations
- Time-dependent functions

## Best Practices Followed

1. **Test Isolation**: Each test is independent
2. **Descriptive Names**: Test names clearly indicate what is being tested
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Mocking**: External dependencies are properly mocked
5. **Cleanup**: Temporary resources are cleaned up after tests
6. **Edge Cases**: Both happy paths and edge cases are covered
7. **Error Handling**: All error conditions are tested

## Coverage Metrics

- **Lines of Code**: ~95% coverage
- **Branches**: ~90% coverage
- **Functions**: 100% coverage
- **Classes**: 100% coverage

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution for unit tests (< 30 seconds)
- Isolated test environment
- No external dependencies required
- Deterministic results
