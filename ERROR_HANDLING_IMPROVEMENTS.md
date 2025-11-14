# Error Handling Improvements - OpenFGA Python SDK

## Summary

This document outlines the improvements made to error handling in the OpenFGA Python SDK. These changes make errors easier to work with, more informative, and less verbose to handle.

## What Changed

### 1. Convenience Properties

Instead of nested access patterns, errors now provide direct property access.

#### Before (Old Way)
```python
try:
    client.check(...)
except ApiException as e:
    # Verbose nested access
    code = e.parsed_exception.code if e.parsed_exception else None
    message = e.parsed_exception.message if e.parsed_exception else None
    request_id = e.header.get('fga-request-id')
    store_id = e.header.get('store_id')
    model_id = e.header.get('openfga_authorization_model_id')
```

#### After (New Way)
```python
try:
    client.check(...)
except ApiException as e:
    # Direct, clean access
    code = e.code
    message = e.error_message
    request_id = e.request_id
    store_id = e.store_id
    model_id = e.authorization_model_id
```

### 2. Helper Methods for Error Classification

No more manual type checking or status code comparisons.

#### Before (Old Way)
```python
try:
    client.write(...)
except ApiException as e:
    # Manual type checking
    if isinstance(e, ValidationException):
        # Handle validation error
        pass
    elif isinstance(e, NotFoundException):
        # Handle not found
        pass
    elif e.status == 429:
        # Handle rate limit
        pass
    elif e.status >= 500:
        # Handle server error
        pass
```

#### After (New Way)
```python
try:
    client.write(...)
except ApiException as e:
    # Clean, semantic methods
    if e.is_validation_error():
        # Handle validation error
        pass
    elif e.is_not_found_error():
        # Handle not found
        pass
    elif e.is_rate_limit_error():
        # Handle rate limit
        pass
    elif e.is_server_error():
        # Handle server error
        pass
    elif e.is_retryable():
        # Retry the operation
        pass
```

### 3. Enhanced Error Messages

Error messages now include comprehensive context.

#### Before (Old Way)
```
(400)
Reason: Bad Request
HTTP response body: {"code":"validation_error","message":"Invalid tuple format"}
```

#### After (New Way)
```
Operation: Check
Status: 400
Error Code: validation_error
Message: Invalid tuple format
Request ID: abc-123-def-456
Store ID: 01HXXX...
Authorization Model ID: 01GYYY...
```

### 4. Operation Context

Errors now track which operation failed, making debugging much easier. Operation names are **automatically extracted** from telemetry attributes - no manual configuration needed!

```python
try:
    await client.check(...)
except ApiException as e:
    print(f"Operation '{e.operation_name}' failed")
    # Output: Operation 'check' failed

try:
    await client.write(...)
except ApiException as e:
    print(f"Operation '{e.operation_name}' failed")
    # Output: Operation 'write' failed
```

**How it works:**
- The auto-generated `open_fga_api.py` passes telemetry attributes to every call
- These attributes include `fga_client_request_method` (e.g., "check", "write")
- `api_client.py` automatically extracts the operation name from telemetry
- All exceptions get the operation name set automatically
- No changes needed to generated code!

## Available Properties

All `ApiException` instances now have these properties:

| Property | Type | Description |
|----------|------|-------------|
| `code` | `str \| None` | Error code (e.g., "validation_error") |
| `error_message` | `str \| None` | Human-readable error message |
| `request_id` | `str \| None` | FGA request ID for tracing |
| `store_id` | `str \| None` | Store ID context |
| `authorization_model_id` | `str \| None` | Authorization model ID context |
| `operation_name` | `str \| None` | Operation that failed - auto-extracted from telemetry (e.g., "check", "write", "expand") |

## Available Helper Methods

All `ApiException` instances now have these methods:

| Method | Returns | Description |
|--------|---------|-------------|
| `is_validation_error()` | `bool` | True if this is a validation error (4xx) |
| `is_not_found_error()` | `bool` | True if this is a not found error (404) |
| `is_authentication_error()` | `bool` | True if this is an authentication error (401) |
| `is_authorization_error()` | `bool` | True if this is an authorization error (403) |
| `is_rate_limit_error()` | `bool` | True if this is a rate limit error (429) |
| `is_server_error()` | `bool` | True if this is a server error (5xx) |
| `is_retryable()` | `bool` | True if this error should be retried |

## Backward Compatibility

All changes are **fully backward compatible**. Existing code continues to work without modifications:

```python
# Old code still works
try:
    client.check(...)
except ApiException as e:
    if e.parsed_exception:
        code = e.parsed_exception.code  # Still works!
    request_id = e.header.get('fga-request-id')  # Still works!
```

## Testing

### Unit Tests
Run the comprehensive unit test suite:
```bash
python -m unittest test.error_handling_improvements_test -v
```

17 test cases verify:
- Convenience properties work correctly
- Helper methods classify errors properly
- Enhanced error messages include all context
- Backward compatibility is maintained

### Integration Tests
Run tests against a real OpenFGA server:
```bash
# Start OpenFGA server
docker compose -f docker-compose.integration-test.yml up -d

# Run integration tests
python -m unittest test.integration_error_handling_test -v

# Or use the helper script
./run_integration_tests.sh
```

Integration tests demonstrate:
- Real error scenarios with live server
- All new features working end-to-end
- Practical examples of improved error handling

See `test/README_INTEGRATION_TESTS.md` for detailed testing instructions.

## Example: Complete Error Handling Pattern

Here's a complete example showing how to use the new features:

```python
from openfga_sdk import OpenFgaClient
from openfga_sdk.exceptions import ApiException
import asyncio

async def main():
    client = OpenFgaClient(...)

    try:
        result = await client.check(
            body=CheckRequest(
                tuple_key=TupleKey(
                    user="user:anne",
                    relation="reader",
                    object="document:budget"
                )
            )
        )
    except ApiException as e:
        # Use convenient properties
        print(f"Operation: {e.operation_name}")
        print(f"Error Code: {e.code}")
        print(f"Message: {e.error_message}")
        print(f"Request ID: {e.request_id}")

        # Use helper methods for control flow
        if e.is_validation_error():
            print("Fix your request and try again")
        elif e.is_authentication_error():
            print("Check your credentials")
        elif e.is_rate_limit_error():
            print("Slow down and retry")
        elif e.is_retryable():
            print("Temporary issue, retrying...")
            # Implement retry logic
        else:
            print("Unrecoverable error")
            raise

        # Or just print the enhanced error message
        print(str(e))

asyncio.run(main())
```

## Migration Guide

No migration needed! But you can improve your existing code:

### Quick Wins

1. **Replace nested access with properties:**
   ```python
   # Before
   code = e.parsed_exception.code if e.parsed_exception else None
   # After
   code = e.code
   ```

2. **Use helper methods instead of type checks:**
   ```python
   # Before
   if isinstance(e, ValidationException):
   # After
   if e.is_validation_error():
   ```

3. **Leverage enhanced error messages:**
   ```python
   # Before
   print(f"Error {e.status}: {e.reason}")
   # After
   print(str(e))  # Much more informative!
   ```

## Implementation Details

### Files Modified

1. **openfga_sdk/exceptions.py**
   - Added `operation_name` parameter to all exception classes
   - Added convenience properties: `code`, `error_message`, `request_id`, `store_id`, `authorization_model_id`
   - Added helper methods: `is_validation_error()`, `is_not_found_error()`, etc.
   - Enhanced `__str__()` method with comprehensive formatting

2. **openfga_sdk/api_client.py**
   - Added `_operation_name` parameter to `call_api()` and `__call_api()` methods
   - Set `operation_name` on exceptions before raising

3. **openfga_sdk/sync/api_client.py**
   - Same changes as async version for synchronous client

### Design Principles

- **Backward Compatibility:** All existing code continues to work
- **No Breaking Changes:** Only additive changes
- **Pythonic:** Uses properties and methods, not nested data structures
- **Type Safe:** All properties and methods properly typed
- **Well Tested:** 17 unit tests + integration tests

## Benefits

✅ **Less Verbose:** Direct property access instead of nested conditionals
✅ **More Readable:** Semantic helper methods instead of type checking
✅ **Better DX:** Enhanced error messages with full context
✅ **Easier Debugging:** Operation names show what failed
✅ **Safer:** Type hints and proper error classification
✅ **Backward Compatible:** No breaking changes

## Questions?

See `test/error_handling_improvements_test.py` for comprehensive examples of all features.
See `test/integration_error_handling_test.py` for real-world usage patterns.
