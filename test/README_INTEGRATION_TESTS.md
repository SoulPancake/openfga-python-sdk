# Integration Tests for Error Handling

This directory contains integration tests that validate the improved error handling functionality in the OpenFGA Python SDK.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- OpenFGA Python SDK installed in development mode

## Running the Tests

### 1. Start OpenFGA Server

Start an OpenFGA server using Docker:

```bash
docker compose -f docker-compose.integration-test.yml up -d
```

Wait for the server to be ready (the healthcheck will ensure it's up):

```bash
docker compose -f docker-compose.integration-test.yml ps
```

### 2. Run Integration Tests

```bash
# From the repository root
python -m pytest test/integration_error_handling_test.py -v -s

# Or using unittest
python -m unittest test.integration_error_handling_test -v
```

### 3. Stop OpenFGA Server

```bash
docker compose -f docker-compose.integration-test.yml down
```

## What These Tests Demonstrate

The integration tests showcase the following improvements to error handling:

### 1. **Convenience Properties**
Instead of nested access patterns:
```python
# OLD WAY
code = e.parsed_exception.code if e.parsed_exception else None
message = e.parsed_exception.message if e.parsed_exception else None
request_id = e.header.get('fga-request-id')
```

Now you can use direct properties:
```python
# NEW WAY
code = e.code
message = e.error_message
request_id = e.request_id
```

### 2. **Helper Methods**
Easily categorize errors:
```python
if e.is_validation_error():
    # Handle validation error
elif e.is_not_found_error():
    # Handle not found
elif e.is_retryable():
    # Retry the operation
```

### 3. **Enhanced Error Messages**
Errors now display comprehensive context:
```
Operation: Check
Status: 400
Error Code: validation_error
Message: Invalid user format
Request ID: abc-123-def-456
Store ID: 01HXXX...
Authorization Model ID: 01GYYY...
```

### 4. **Operation Context**
Errors now include the operation name that failed, making debugging easier.

## Test Scenarios

The integration tests cover:

1. **Validation Errors** - Invalid user format in check requests
2. **Not Found Errors** - Reading non-existent tuples
3. **Invalid Relations** - Writing tuples with undefined relations
4. **Invalid Model IDs** - Using non-existent authorization models
5. **Helper Methods** - Comprehensive testing of all error categorization methods
6. **Access Pattern Comparison** - Side-by-side comparison of old vs new patterns

## Environment Variables

- `OPENFGA_API_URL`: OpenFGA server URL (default: `http://localhost:8080`)

## Troubleshooting

If tests fail with connection errors:
1. Verify OpenFGA is running: `docker compose -f docker-compose.integration-test.yml ps`
2. Check server health: `curl http://localhost:8080/healthz`
3. View logs: `docker compose -f docker-compose.integration-test.yml logs`

If you see "command not found" errors for docker commands, ensure Docker is installed and running.
