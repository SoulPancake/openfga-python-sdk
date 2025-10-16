# Conflict Options Example

This example demonstrates the `on_duplicate` and `on_missing` conflict options for write operations in the OpenFGA Python SDK.

## Overview

OpenFGA v1.10.0 introduced support for conflict options that control the behavior when:
- Writing a tuple that already exists (`on_duplicate`)
- Deleting a tuple that doesn't exist (`on_missing`)

These options help avoid unnecessary error handling logic in client-side code and improve performance by reducing retry scenarios.

## Prerequisites

- OpenFGA server v1.10.0 or later running on `localhost:8080`
- Python 3.10 or later
- The OpenFGA Python SDK installed

## Running the Example

```bash
python example.py
```

The example will:
1. Create a temporary store and authorization model
2. Demonstrate each conflict option scenario with clear checkpoints:
   - Default behavior (ERROR mode) for duplicate writes
   - IGNORE mode for duplicate writes
   - Default behavior (ERROR mode) for missing deletes
   - IGNORE mode for missing deletes
   - Combined usage of both options
   - Explicit ERROR mode configuration
3. Clean up the temporary store

## Conflict Options

### `on_duplicate` (for writes)

Controls behavior when writing a tuple that already exists:

- **ERROR** (default): Returns an error if an identical tuple already exists
- **IGNORE**: Treats duplicate writes as no-ops (no error thrown)

### `on_missing` (for deletes)

Controls behavior when deleting a tuple that doesn't exist:

- **ERROR** (default): Returns an error if the tuple doesn't exist
- **IGNORE**: Treats deletes of non-existent tuples as no-ops (no error thrown)

## Usage Examples

### Ignoring Duplicate Writes

```python
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnDuplicateWrites,
    ConflictOptions,
)

options = {
    "conflict": ConflictOptions(
        on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE
    )
}

await openfga.write_tuples([tuple_to_write], options)
```

### Ignoring Missing Deletes

```python
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnMissingDeletes,
    ConflictOptions,
)

options = {
    "conflict": ConflictOptions(
        on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE
    )
}

await openfga.delete_tuples([tuple_to_delete], options)
```

### Using Both Options Together

```python
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnDuplicateWrites,
    ClientWriteRequestOnMissingDeletes,
    ConflictOptions,
)
from openfga_sdk.client.models.write_request import ClientWriteRequest

options = {
    "conflict": ConflictOptions(
        on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
        on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
    )
}

await openfga.write(
    ClientWriteRequest(writes=[...], deletes=[...]),
    options
)
```

## Benefits

1. **Reduced Error Handling**: No need to catch and handle errors for duplicate writes or missing deletes
2. **Improved Performance**: Eliminates retry logic and reduces request latency
3. **Idempotent Operations**: Makes write operations idempotent, simplifying client code
4. **Better Developer Experience**: Less boilerplate code and cleaner API usage

## Additional Resources

- [OpenFGA Documentation](https://openfga.dev/docs)
- [OpenFGA API Reference](https://openfga.dev/api/service)
- [OpenFGA Roadmap - Write Conflict Options](https://github.com/openfga/roadmap/issues/31)
