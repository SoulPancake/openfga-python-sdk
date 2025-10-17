# OpenFGA Conflict Options Example

This example demonstrates all permutations and combinations of conflict options for write operations in the OpenFGA Python SDK.

## Overview

OpenFGA v1.10.0 introduced support for handling duplicate writes and missing deletes gracefully through conflict options:

- **`on_duplicate_writes`**: Controls behavior when writing a tuple that already exists
  - `ERROR` - Returns an error on duplicates (default)
  - `IGNORE` - Silently skips duplicate writes

- **`on_missing_deletes`**: Controls behavior when deleting a tuple that doesn't exist
  - `ERROR` - Returns an error on missing deletes (default)
  - `IGNORE` - Silently skips missing deletes

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- OpenFGA Python SDK installed

## Quick Start

### 1. Start OpenFGA Server

```bash
make start
```

This will start:
- PostgreSQL database on port 5432
- OpenFGA server on port 8080
- OpenFGA Playground on port 3000

### 2. Run the Demo

```bash
make run
```

This will execute all 8 test scenarios demonstrating different combinations of conflict options.

### 3. Stop the Server

```bash
make stop
```

## Test Scenarios

The demo runs the following test scenarios:

1. **Duplicate Write with ERROR** (default behavior)
   - First write succeeds
   - Second identical write fails with error

2. **Duplicate Write with IGNORE**
   - First write succeeds
   - Second identical write succeeds silently

3. **Missing Delete with ERROR** (default behavior)
   - Deleting non-existent tuple fails with error

4. **Missing Delete with IGNORE**
   - Deleting non-existent tuple succeeds silently

5. **Both Options Set to IGNORE**
   - Duplicate writes are ignored
   - Missing deletes are ignored

6. **Both Options Set to ERROR** (default behavior)
   - Duplicate writes cause errors
   - Missing deletes cause errors

7. **IGNORE Duplicates, ERROR on Missing**
   - Duplicate writes succeed silently
   - Missing deletes cause errors

8. **ERROR on Duplicates, IGNORE Missing**
   - Duplicate writes cause errors
   - Missing deletes succeed silently

## Available Make Targets

```bash
make help     # Show available commands
make start    # Start OpenFGA server and database
make stop     # Stop OpenFGA server and database
make status   # Check status of services
make run      # Run the conflict options demo
make logs     # Show logs from OpenFGA server
make clean    # Stop services and remove volumes
make demo     # Start services, run demo, keep running
```

## Manual Execution

If you prefer to run the services and demo manually:

```bash
# Start services
docker compose up -d

# Wait for services to be ready (10-15 seconds)
sleep 10

# Run the demo
python3 conflict_options_example.py

# Stop services
docker compose down
```

## Environment Variables

You can customize the API URL:

```bash
export FGA_API_URL=http://localhost:8080
python3 conflict_options_example.py
```

## Code Example

Here's a snippet showing how to use conflict options:

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnDuplicateWrites,
    ClientWriteRequestOnMissingDeletes,
    ConflictOptions,
)

# Configure options
options = {
    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
    "conflict": ConflictOptions(
        on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
        on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
    )
}

# Write with conflict options
body = ClientWriteRequest(
    writes=[
        ClientTuple(
            user="user:alice",
            relation="viewer",
            object="document:budget",
        ),
    ],
)

async with OpenFgaClient(configuration) as client:
    # This will succeed even if the tuple already exists
    response = await client.write(body, options)
```

## Notes

- This example requires OpenFGA server v1.10.0 or later
- Default behavior (when options are not specified) is to return errors on duplicates and missing deletes
- The demo creates a temporary store and cleans it up after completion
- All test scenarios are independent and demonstrate different combinations

## Troubleshooting

### Services won't start
- Ensure Docker is running
- Check if ports 8080, 3000, and 5432 are available
- Try `make clean` to remove old volumes

### Demo fails to connect
- Ensure services are running: `make status`
- Wait a few more seconds for OpenFGA to be ready
- Check logs: `make logs`

### Python dependencies missing
- Ensure the SDK is installed: `pip install openfga-sdk`
- Or install from the repository root: `pip install -e .`

## Learn More

- [OpenFGA Documentation](https://openfga.dev/docs)
- [Python SDK Documentation](https://github.com/openfga/python-sdk)
- [OpenFGA API Reference](https://openfga.dev/api/service)
