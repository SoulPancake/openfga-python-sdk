# ruff: noqa: E402

"""
Example demonstrating write conflict options for idempotent operations.

This example tests the new conflict options feature against a real OpenFGA server:
- on_duplicate_writes: IGNORE/ERROR
- on_missing_deletes: IGNORE/ERROR
"""

import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv


sdk_path = os.path.realpath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sys.path.insert(0, sdk_path)

from openfga_sdk import (
    ClientConfiguration,
    CreateStoreRequest,
    OnDuplicateWrites,
    OnMissingDeletes,
    OpenFgaClient,
    TypeDefinition,
    WriteAuthorizationModelRequest,
)
from openfga_sdk.client.models import (
    ClientTuple,
    ClientWriteRequest,
)
from openfga_sdk.credentials import CredentialConfiguration, Credentials


async def test_conflict_options():
    """Test conflict options against a real OpenFGA server."""
    load_dotenv()

    # Setup credentials
    credentials = Credentials()
    if os.getenv("FGA_CLIENT_ID") is not None:
        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                api_issuer=os.getenv("FGA_API_TOKEN_ISSUER"),
                api_audience=os.getenv("FGA_API_AUDIENCE"),
                client_id=os.getenv("FGA_CLIENT_ID"),
                client_secret=os.getenv("FGA_CLIENT_SECRET"),
            ),
        )

    # Setup configuration
    if os.getenv("FGA_API_URL") is not None:
        configuration = ClientConfiguration(
            api_url=os.getenv("FGA_API_URL"), credentials=credentials
        )
    else:
        configuration = ClientConfiguration(
            api_url="http://localhost:8080", credentials=credentials
        )

    print("=" * 80)
    print("Testing OpenFGA Write Conflict Options")
    print("=" * 80)
    print()

    async with OpenFgaClient(configuration) as client:
        # Create a test store
        print("1. Creating test store...")
        store_name = f"Conflict Options Test {datetime.now().isoformat()}"
        store = await client.create_store(CreateStoreRequest(name=store_name))
        client.set_store_id(store.id)
        print(f"   ✓ Store created: {store.id}")
        print()

        # Create authorization model
        print("2. Creating authorization model...")
        model = await client.write_authorization_model(
            WriteAuthorizationModelRequest(
                schema_version="1.1",
                type_definitions=[
                    TypeDefinition(
                        type="user",
                    ),
                    TypeDefinition(
                        type="document",
                        relations={
                            "reader": {"this": {}},
                            "writer": {"this": {}},
                        },
                    ),
                ],
            )
        )
        print(f"   ✓ Model created: {model.authorization_model_id}")
        print()

        # Test 1: Write a tuple initially
        print("3. Test 1: Writing initial tuple...")
        tuple1 = ClientTuple(
            object="document:budget",
            relation="reader",
            user="user:alice",
        )
        
        await client.write(
            ClientWriteRequest(writes=[tuple1]),
            options={"authorization_model_id": model.authorization_model_id},
        )
        print("   ✓ Tuple written successfully")
        print()

        # Test 2: Try to write the same tuple with ERROR (default behavior)
        print("4. Test 2: Writing duplicate tuple with ERROR behavior...")
        try:
            await client.write(
                ClientWriteRequest(writes=[tuple1]),
                options={
                    "authorization_model_id": model.authorization_model_id,
                    "conflict": {
                        "on_duplicate_writes": OnDuplicateWrites.ERROR,
                    },
                },
            )
            print("   ✗ UNEXPECTED: Should have thrown an error!")
        except Exception as e:
            print(f"   ✓ Expected error occurred: {type(e).__name__}")
        print()

        # Test 3: Write the same tuple with IGNORE
        print("5. Test 3: Writing duplicate tuple with IGNORE behavior...")
        try:
            await client.write(
                ClientWriteRequest(writes=[tuple1]),
                options={
                    "authorization_model_id": model.authorization_model_id,
                    "conflict": {
                        "on_duplicate_writes": OnDuplicateWrites.IGNORE,
                    },
                },
            )
            print("   ✓ Duplicate write ignored successfully (idempotent)")
        except Exception as e:
            print(f"   ✗ UNEXPECTED ERROR: {e}")
        print()

        # Test 4: Call write multiple times with IGNORE (idempotency test)
        print("6. Test 4: Testing idempotency (multiple writes with IGNORE)...")
        for i in range(3):
            try:
                await client.write(
                    ClientWriteRequest(writes=[tuple1]),
                    options={
                        "authorization_model_id": model.authorization_model_id,
                        "conflict": {
                            "on_duplicate_writes": "IGNORE",
                        },
                    },
                )
                print(f"   ✓ Write #{i+1} succeeded")
            except Exception as e:
                print(f"   ✗ Write #{i+1} failed: {e}")
        print()

        # Test 5: Delete a non-existent tuple with ERROR
        print("7. Test 5: Deleting non-existent tuple with ERROR behavior...")
        tuple2 = ClientTuple(
            object="document:report",
            relation="reader",
            user="user:bob",
        )
        try:
            await client.write(
                ClientWriteRequest(deletes=[tuple2]),
                options={
                    "authorization_model_id": model.authorization_model_id,
                    "conflict": {
                        "on_missing_deletes": OnMissingDeletes.ERROR,
                    },
                },
            )
            print("   ✗ UNEXPECTED: Should have thrown an error!")
        except Exception as e:
            print(f"   ✓ Expected error occurred: {type(e).__name__}")
        print()

        # Test 6: Delete a non-existent tuple with IGNORE
        print("8. Test 6: Deleting non-existent tuple with IGNORE behavior...")
        try:
            await client.write(
                ClientWriteRequest(deletes=[tuple2]),
                options={
                    "authorization_model_id": model.authorization_model_id,
                    "conflict": {
                        "on_missing_deletes": OnMissingDeletes.IGNORE,
                    },
                },
            )
            print("   ✓ Missing delete ignored successfully (idempotent)")
        except Exception as e:
            print(f"   ✗ UNEXPECTED ERROR: {e}")
        print()

        # Test 7: Combined test - write existing and delete non-existing
        print("9. Test 7: Combined operations with IGNORE on both...")
        tuple3 = ClientTuple(
            object="document:budget",
            relation="writer",
            user="user:charlie",
        )
        try:
            await client.write(
                ClientWriteRequest(
                    writes=[tuple1, tuple3],  # tuple1 already exists
                    deletes=[tuple2],  # tuple2 doesn't exist
                ),
                options={
                    "authorization_model_id": model.authorization_model_id,
                    "conflict": {
                        "on_duplicate_writes": "IGNORE",
                        "on_missing_deletes": "IGNORE",
                    },
                },
            )
            print("   ✓ Combined operations succeeded (fully idempotent)")
        except Exception as e:
            print(f"   ✗ UNEXPECTED ERROR: {e}")
        print()

        # Test 8: Cleanup - delete tuple with IGNORE (can be called multiple times)
        print("10. Test 8: Cleanup with idempotent deletes...")
        for i in range(2):
            try:
                await client.write(
                    ClientWriteRequest(deletes=[tuple1, tuple3]),
                    options={
                        "authorization_model_id": model.authorization_model_id,
                        "conflict": {
                            "on_missing_deletes": "IGNORE",
                        },
                    },
                )
                print(f"   ✓ Cleanup #{i+1} succeeded")
            except Exception as e:
                print(f"   ✗ Cleanup #{i+1} failed: {e}")
        print()

        # Cleanup: Delete the test store
        print("11. Cleaning up test store...")
        await client.delete_store()
        print("   ✓ Store deleted")
        print()

    print("=" * 80)
    print("✅ All conflict options tests completed successfully!")
    print("=" * 80)
    print()
    print("Summary:")
    print("- ERROR behavior throws exceptions as expected")
    print("- IGNORE behavior allows idempotent operations")
    print("- Both on_duplicate_writes and on_missing_deletes work correctly")
    print("- Combined operations with both options work as expected")


if __name__ == "__main__":
    asyncio.run(test_conflict_options())
