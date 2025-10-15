# Write Conflict Options Example

This example demonstrates the new write conflict options feature for idempotent operations in OpenFGA v1.10.0+.

## What This Example Tests

This example tests the conflict options against a **real OpenFGA server** (not mocks):

1. **Duplicate Write Handling (`on_duplicate_writes`)**
   - `ERROR`: Throws an exception when attempting to write an existing tuple (default behavior)
   - `IGNORE`: Silently skips duplicate writes, allowing idempotent operations

2. **Missing Delete Handling (`on_missing_deletes`)**
   - `ERROR`: Throws an exception when attempting to delete a non-existent tuple (default behavior)
   - `IGNORE`: Silently skips missing deletes, allowing idempotent cleanup

3. **Combined Operations**
   - Tests using both options together in a single write request
   - Verifies idempotency by calling the same operations multiple times

## Prerequisites

### Option 1: Local OpenFGA Server

Run OpenFGA locally using Docker:

```bash
docker run -p 8080:8080 openfga/openfga run
```

### Option 2: OpenFGA Cloud

Set environment variables for OpenFGA Cloud:

```bash
export FGA_API_URL="https://api.us1.fga.dev"
export FGA_CLIENT_ID="your-client-id"
export FGA_CLIENT_SECRET="your-client-secret"
export FGA_API_TOKEN_ISSUER="https://auth.us1.fga.dev"
export FGA_API_AUDIENCE="https://api.us1.fga.dev"
```

Or create a `.env` file in this directory with the same variables.

## Running the Example

From the repository root:

```bash
# Install dependencies (if not already done)
uv sync

# Run the example
uv run python example/conflict-options/test_conflict_options.py
```

Or from this directory:

```bash
python test_conflict_options.py
```

## Expected Output

The example will:

1. Create a test store
2. Create an authorization model
3. Test writing duplicate tuples with ERROR behavior (should fail)
4. Test writing duplicate tuples with IGNORE behavior (should succeed)
5. Test idempotency by writing the same tuple multiple times with IGNORE
6. Test deleting non-existent tuples with ERROR behavior (should fail)
7. Test deleting non-existent tuples with IGNORE behavior (should succeed)
8. Test combined operations with both conflict options
9. Test idempotent cleanup operations
10. Delete the test store

You should see output like:

```
================================================================================
Testing OpenFGA Write Conflict Options
================================================================================

1. Creating test store...
   ✓ Store created: 01JAEQF7XXXXXXXXXXX

2. Creating authorization model...
   ✓ Model created: 01JAEQF7XXXXXXXXXXX

3. Test 1: Writing initial tuple...
   ✓ Tuple written successfully

4. Test 2: Writing duplicate tuple with ERROR behavior...
   ✓ Expected error occurred: ApiException

5. Test 3: Writing duplicate tuple with IGNORE behavior...
   ✓ Duplicate write ignored successfully (idempotent)

...

================================================================================
✅ All conflict options tests completed successfully!
================================================================================
```

## What This Proves

This example demonstrates that the implementation:

1. ✅ Works correctly against a real OpenFGA server (not just mocks)
2. ✅ Properly handles duplicate writes with both ERROR and IGNORE options
3. ✅ Properly handles missing deletes with both ERROR and IGNORE options
4. ✅ Enables true idempotent operations
5. ✅ Supports combined operations with multiple conflict options
6. ✅ Follows the OpenFGA v1.10.0 specification

## Code Structure

The example is structured to be:
- **Self-contained**: Creates its own test store and model
- **Comprehensive**: Tests all combinations of conflict options
- **Clear**: Each test is labeled and shows expected vs actual behavior
- **Clean**: Removes the test store at the end

## Use Cases Demonstrated

1. **Idempotent Writes**: Write the same tuple multiple times without errors
2. **Idempotent Deletes**: Delete tuples that may or may not exist
3. **Retry Safety**: Operations can be safely retried without side effects
4. **Batch Operations**: Write and delete multiple tuples with mixed existence states
