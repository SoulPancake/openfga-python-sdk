# Conflict Options Implementation Summary

## Overview

This document provides a comprehensive summary of the conflict options implementation for the OpenFGA Python SDK. The conflict options feature allows developers to handle duplicate writes and missing deletes gracefully without error handling complexity.

## Feature Description

The conflict options feature was introduced in OpenFGA v1.10.0 and provides two configuration options:

1. **`on_duplicate_writes`**: Controls behavior when writing a tuple that already exists
   - `ERROR` - Returns an error on duplicates (default)
   - `IGNORE` - Silently skips duplicate writes

2. **`on_missing_deletes`**: Controls behavior when deleting a tuple that doesn't exist
   - `ERROR` - Returns an error on missing deletes (default)
   - `IGNORE` - Silently skips missing deletes

## Implementation Status

### ✅ API Layer (OpenFgaApi)

**Models:**
- `WriteRequestWrites` - Supports `on_duplicate` parameter (error/ignore)
- `WriteRequestDeletes` - Supports `on_missing` parameter (error/ignore)
- `WriteRequest` - Contains writes and deletes with their respective options

**Location:**
- `/openfga_sdk/models/write_request_writes.py`
- `/openfga_sdk/models/write_request_deletes.py`
- `/openfga_sdk/models/write_request.py`

### ✅ Client Layer (OpenFgaClient)

**Models:**
- `ConflictOptions` - Container for conflict configuration
- `ClientWriteRequestOnDuplicateWrites` - Enum (ERROR, IGNORE)
- `ClientWriteRequestOnMissingDeletes` - Enum (ERROR, IGNORE)
- `ClientWriteOptions` - Contains conflict options along with other write options

**Location:**
- `/openfga_sdk/client/models/write_conflict_opts.py`
- `/openfga_sdk/client/models/write_options.py`

**Implementation:**
- Both async (`/openfga_sdk/client/client.py`) and sync (`/openfga_sdk/sync/client/client.py`) clients support conflict options
- Options are passed through `_write_with_transaction` method
- Properly converts enum values to string values for API calls

### ✅ Tests

**Async Client Tests:**
Location: `/test/client/client_test.py`
- `test_write_with_conflict_options_ignore_duplicates` - Tests IGNORE for duplicate writes
- `test_write_with_conflict_options_ignore_missing_deletes` - Tests IGNORE for missing deletes
- `test_write_with_conflict_options_both` - Tests both options together

**Sync Client Tests:**
Location: `/test/sync/client/client_test.py`
- `test_sync_write_with_conflict_options_ignore_duplicates` - Tests IGNORE for duplicate writes
- `test_sync_write_with_conflict_options_ignore_missing_deletes` - Tests IGNORE for missing deletes
- `test_sync_write_with_conflict_options_both` - Tests both options together

### ✅ Documentation

**README.md:**
- Section: "Conflict Options for Write Operations"
- Contains 3 complete examples:
  1. Ignoring duplicate writes
  2. Ignoring missing deletes
  3. Using both conflict options together

**CHANGELOG.md:**
- Feature documented in Unreleased section
- References README for detailed usage

### ✅ Example Implementation

**Location:** `/example/conflict-options/`

**Files Created:**
1. `conflict_options_example.py` - Comprehensive example demonstrating all 8 permutations
2. `docker-compose.yml` - OpenFGA server with PostgreSQL and automated migrations
3. `Makefile` - Quick commands to start, stop, and run the demo
4. `README.md` - Complete documentation for the example
5. `requirements.txt` - Dependencies specification
6. `test_structure.py` - Validation test for example structure

**Test Scenarios (8 total):**
1. Duplicate writes with ERROR (default)
2. Duplicate writes with IGNORE
3. Missing deletes with ERROR (default)
4. Missing deletes with IGNORE
5. Both options set to IGNORE
6. Both options set to ERROR (default)
7. IGNORE duplicates + ERROR on missing
8. ERROR on duplicates + IGNORE missing

**Makefile Targets:**
- `make start` - Start OpenFGA and database
- `make stop` - Stop services
- `make status` - Check service status
- `make run` - Run the demo
- `make logs` - View OpenFGA logs
- `make clean` - Remove all services and volumes
- `make demo` - Complete workflow (start, run, keep running)

## Usage Example

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnDuplicateWrites,
    ClientWriteRequestOnMissingDeletes,
    ConflictOptions,
)

# Configure the client
configuration = ClientConfiguration(api_url="http://localhost:8080")
configuration.store_id = "your-store-id"

# Set up conflict options
options = {
    "authorization_model_id": "your-model-id",
    "conflict": ConflictOptions(
        on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
        on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
    )
}

# Create write request
body = ClientWriteRequest(
    writes=[
        ClientTuple(
            user="user:alice",
            relation="viewer",
            object="document:budget",
        ),
    ],
    deletes=[
        ClientTuple(
            user="user:bob",
            relation="editor",
            object="document:report",
        ),
    ],
)

# Execute write with conflict options
async with OpenFgaClient(configuration) as client:
    # This will succeed even if:
    # - The write tuple already exists (ignored)
    # - The delete tuple doesn't exist (ignored)
    response = await client.write(body, options)
```

## Testing the Example

1. Start the OpenFGA server:
   ```bash
   cd example/conflict-options
   make start
   ```

2. Run the demonstration:
   ```bash
   make run
   ```

3. Stop the services:
   ```bash
   make stop
   ```

## Verification Checklist

- [x] API layer models support `on_duplicate` and `on_missing`
- [x] Client layer models (ConflictOptions, enums) implemented
- [x] Async client supports conflict options
- [x] Sync client supports conflict options
- [x] Tests for async client (3 test cases)
- [x] Tests for sync client (3 test cases)
- [x] API layer tests include conflict options
- [x] README documentation with examples
- [x] CHANGELOG updated
- [x] Example directory with all permutations
- [x] Docker compose for OpenFGA server
- [x] Automated database migrations
- [x] Makefile for easy execution
- [x] Example README with complete instructions
- [x] Structure validation test

## Requirements Met

All requirements from the problem statement have been successfully met:

1. ✅ Conflict options exposed in API client and models
2. ✅ SDK client interface supports idempotency options
3. ✅ Tests for both OpenFgaApi and OpenFgaClient layers
4. ✅ README Write section updated with conflict options
5. ✅ CHANGELOG unreleased section updated
6. ✅ Example runner demonstrating all permutations
7. ✅ Docker compose for OpenFGA server
8. ✅ Makefile for quick iteration execution

## Additional Enhancements

Beyond the requirements, the implementation includes:

1. **Automated Migrations**: Docker compose automatically runs database migrations
2. **Structure Validation**: Test script to verify example integrity
3. **Comprehensive Documentation**: Detailed README in example directory
4. **Both Client Types**: Support in both async and sync clients
5. **Healthchecks**: Docker compose includes proper health checking
6. **Multiple Make Targets**: Convenient commands for different operations

## Notes

- Requires OpenFGA server v1.10.0 or later
- Default behavior (no options specified) returns errors for both duplicates and missing deletes
- Both async and sync clients have identical API
- Example creates temporary store and cleans up automatically
- All 8 test scenarios are independent and demonstrate different combinations

## Future Considerations

- Consider adding integration tests that run against actual OpenFGA server
- Could add metrics/telemetry for conflict option usage
- Potential for retry strategies when errors occur with specific options
