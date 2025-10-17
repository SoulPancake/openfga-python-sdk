#!/usr/bin/env python3
# ruff: noqa: E402

"""
Python SDK for OpenFGA - Conflict Options Example

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

This example demonstrates all permutations of conflict options:
- on_duplicate_writes: ERROR, IGNORE
- on_missing_deletes: ERROR, IGNORE
"""

import asyncio
import os
import sys
from typing import Optional

# Add the SDK path
sdk_path = os.path.realpath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sys.path.insert(0, sdk_path)

from openfga_sdk import (
    ClientConfiguration,
    CreateStoreRequest,
    OpenFgaClient,
    TypeDefinition,
    Userset,
    WriteAuthorizationModelRequest,
)
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnDuplicateWrites,
    ClientWriteRequestOnMissingDeletes,
    ConflictOptions,
)


class ConflictOptionsDemo:
    """Demonstrates conflict options for write operations."""

    def __init__(self, api_url: str = "http://localhost:8080"):
        """Initialize the demo with the OpenFGA API URL."""
        self.api_url = api_url
        self.store_id: Optional[str] = None
        self.model_id: Optional[str] = None
        self.client: Optional[OpenFgaClient] = None

    async def setup(self):
        """Set up the OpenFGA store and authorization model."""
        print("=" * 80)
        print("Setting up OpenFGA store and authorization model")
        print("=" * 80)

        configuration = ClientConfiguration(api_url=self.api_url)
        self.client = OpenFgaClient(configuration)

        # Create store
        print("\n1. Creating store...")
        store_response = await self.client.create_store(
            CreateStoreRequest(name="Conflict Options Demo Store")
        )
        self.store_id = store_response.id
        self.client.set_store_id(self.store_id)
        print(f"   ✓ Store created with ID: {self.store_id}")

        # Create authorization model
        print("\n2. Creating authorization model...")
        model_response = await self.client.write_authorization_model(
            WriteAuthorizationModelRequest(
                schema_version="1.1",
                type_definitions=[
                    TypeDefinition(type="user"),
                    TypeDefinition(
                        type="document",
                        relations={
                            "viewer": Userset(this={}),
                            "editor": Userset(this={}),
                        },
                    ),
                ],
            )
        )
        self.model_id = model_response.authorization_model_id
        self.client.set_authorization_model_id(self.model_id)
        print(f"   ✓ Model created with ID: {self.model_id}")

    async def cleanup(self):
        """Clean up by deleting the store."""
        if self.client and self.store_id:
            print("\n" + "=" * 80)
            print("Cleaning up...")
            print("=" * 80)
            print(f"\nDeleting store {self.store_id}...")
            await self.client.delete_store()
            print("   ✓ Store deleted")
            await self.client.close()

    async def demo_duplicate_write_error(self):
        """Demonstrate duplicate write with ERROR option (default behavior)."""
        print("\n" + "=" * 80)
        print("Test 1: Duplicate Write with ERROR option (default)")
        print("=" * 80)

        tuple_to_write = ClientTuple(
            user="user:alice",
            relation="viewer",
            object="document:test1",
        )

        # First write - should succeed
        print("\n1. Writing tuple for the first time...")
        body = ClientWriteRequest(writes=[tuple_to_write])
        options = {
            "conflict": ConflictOptions(
                on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.ERROR
            )
        }
        response = await self.client.write(body, options)
        print(f"   ✓ First write succeeded")

        # Second write - should fail with error
        print("\n2. Writing the same tuple again (expecting error)...")
        try:
            await self.client.write(body, options)
            print("   ✗ ERROR: Should have failed but succeeded!")
        except Exception as e:
            print(f"   ✓ Got expected error: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}...")

    async def demo_duplicate_write_ignore(self):
        """Demonstrate duplicate write with IGNORE option."""
        print("\n" + "=" * 80)
        print("Test 2: Duplicate Write with IGNORE option")
        print("=" * 80)

        tuple_to_write = ClientTuple(
            user="user:bob",
            relation="viewer",
            object="document:test2",
        )

        # First write - should succeed
        print("\n1. Writing tuple for the first time...")
        body = ClientWriteRequest(writes=[tuple_to_write])
        options = {
            "conflict": ConflictOptions(
                on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE
            )
        }
        response = await self.client.write(body, options)
        print(f"   ✓ First write succeeded")

        # Second write - should succeed silently
        print("\n2. Writing the same tuple again (expecting silent success)...")
        response = await self.client.write(body, options)
        print(f"   ✓ Second write succeeded silently (duplicate ignored)")

    async def demo_missing_delete_error(self):
        """Demonstrate missing delete with ERROR option (default behavior)."""
        print("\n" + "=" * 80)
        print("Test 3: Missing Delete with ERROR option (default)")
        print("=" * 80)

        tuple_to_delete = ClientTuple(
            user="user:charlie",
            relation="viewer",
            object="document:test3",
        )

        # Attempt to delete non-existent tuple - should fail with error
        print("\n1. Deleting a tuple that doesn't exist (expecting error)...")
        body = ClientWriteRequest(deletes=[tuple_to_delete])
        options = {
            "conflict": ConflictOptions(
                on_missing_deletes=ClientWriteRequestOnMissingDeletes.ERROR
            )
        }
        try:
            await self.client.write(body, options)
            print("   ✗ ERROR: Should have failed but succeeded!")
        except Exception as e:
            print(f"   ✓ Got expected error: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}...")

    async def demo_missing_delete_ignore(self):
        """Demonstrate missing delete with IGNORE option."""
        print("\n" + "=" * 80)
        print("Test 4: Missing Delete with IGNORE option")
        print("=" * 80)

        tuple_to_delete = ClientTuple(
            user="user:david",
            relation="viewer",
            object="document:test4",
        )

        # Attempt to delete non-existent tuple - should succeed silently
        print("\n1. Deleting a tuple that doesn't exist (expecting silent success)...")
        body = ClientWriteRequest(deletes=[tuple_to_delete])
        options = {
            "conflict": ConflictOptions(
                on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE
            )
        }
        response = await self.client.write(body, options)
        print(f"   ✓ Delete succeeded silently (missing tuple ignored)")

    async def demo_both_ignore(self):
        """Demonstrate both conflict options set to IGNORE."""
        print("\n" + "=" * 80)
        print("Test 5: Both options set to IGNORE")
        print("=" * 80)

        write_tuple = ClientTuple(
            user="user:eve",
            relation="viewer",
            object="document:test5",
        )
        delete_tuple = ClientTuple(
            user="user:frank",
            relation="viewer",
            object="document:test6",
        )

        # First, write the tuple
        print("\n1. Writing tuple for the first time...")
        body = ClientWriteRequest(writes=[write_tuple])
        options = {
            "conflict": ConflictOptions(
                on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
                on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
            )
        }
        response = await self.client.write(body, options)
        print(f"   ✓ First write succeeded")

        # Try duplicate write and missing delete together
        print("\n2. Duplicate write and missing delete together...")
        body = ClientWriteRequest(writes=[write_tuple], deletes=[delete_tuple])
        response = await self.client.write(body, options)
        print(f"   ✓ Both operations succeeded silently")
        print(f"      - Duplicate write ignored")
        print(f"      - Missing delete ignored")

    async def demo_both_error(self):
        """Demonstrate both conflict options set to ERROR."""
        print("\n" + "=" * 80)
        print("Test 6: Both options set to ERROR (default behavior)")
        print("=" * 80)

        write_tuple = ClientTuple(
            user="user:grace",
            relation="viewer",
            object="document:test7",
        )

        # First, write the tuple
        print("\n1. Writing tuple for the first time...")
        body = ClientWriteRequest(writes=[write_tuple])
        options = {
            "conflict": ConflictOptions(
                on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.ERROR,
                on_missing_deletes=ClientWriteRequestOnMissingDeletes.ERROR,
            )
        }
        response = await self.client.write(body, options)
        print(f"   ✓ First write succeeded")

        # Try duplicate write - should fail
        print("\n2. Attempting duplicate write (expecting error)...")
        try:
            await self.client.write(body, options)
            print("   ✗ ERROR: Should have failed but succeeded!")
        except Exception as e:
            print(f"   ✓ Got expected error: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}...")

    async def demo_mixed_ignore_duplicate_error_missing(self):
        """Demonstrate IGNORE for duplicates, ERROR for missing deletes."""
        print("\n" + "=" * 80)
        print("Test 7: IGNORE duplicates, ERROR on missing deletes")
        print("=" * 80)

        write_tuple = ClientTuple(
            user="user:henry",
            relation="viewer",
            object="document:test8",
        )
        delete_tuple = ClientTuple(
            user="user:iris",
            relation="viewer",
            object="document:test9",
        )

        options = {
            "conflict": ConflictOptions(
                on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
                on_missing_deletes=ClientWriteRequestOnMissingDeletes.ERROR,
            )
        }

        # Write tuple twice
        print("\n1. Writing tuple twice (duplicate should be ignored)...")
        body = ClientWriteRequest(writes=[write_tuple])
        await self.client.write(body, options)
        print(f"   ✓ First write succeeded")
        await self.client.write(body, options)
        print(f"   ✓ Second write succeeded (duplicate ignored)")

        # Try missing delete - should fail
        print("\n2. Attempting to delete non-existent tuple (expecting error)...")
        body = ClientWriteRequest(deletes=[delete_tuple])
        try:
            await self.client.write(body, options)
            print("   ✗ ERROR: Should have failed but succeeded!")
        except Exception as e:
            print(f"   ✓ Got expected error: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}...")

    async def demo_mixed_error_duplicate_ignore_missing(self):
        """Demonstrate ERROR for duplicates, IGNORE for missing deletes."""
        print("\n" + "=" * 80)
        print("Test 8: ERROR on duplicates, IGNORE missing deletes")
        print("=" * 80)

        write_tuple = ClientTuple(
            user="user:jack",
            relation="viewer",
            object="document:test10",
        )
        delete_tuple = ClientTuple(
            user="user:kate",
            relation="viewer",
            object="document:test11",
        )

        options = {
            "conflict": ConflictOptions(
                on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.ERROR,
                on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
            )
        }

        # Write tuple
        print("\n1. Writing tuple for the first time...")
        body = ClientWriteRequest(writes=[write_tuple])
        await self.client.write(body, options)
        print(f"   ✓ First write succeeded")

        # Try duplicate write - should fail
        print("\n2. Attempting duplicate write (expecting error)...")
        try:
            await self.client.write(body, options)
            print("   ✗ ERROR: Should have failed but succeeded!")
        except Exception as e:
            print(f"   ✓ Got expected error: {type(e).__name__}")
            print(f"      Message: {str(e)[:100]}...")

        # Try missing delete - should succeed
        print("\n3. Deleting non-existent tuple (should be ignored)...")
        body = ClientWriteRequest(deletes=[delete_tuple])
        await self.client.write(body, options)
        print(f"   ✓ Delete succeeded (missing tuple ignored)")

    async def run_all_demos(self):
        """Run all demonstration scenarios."""
        try:
            await self.setup()

            # Run all test scenarios
            await self.demo_duplicate_write_error()
            await self.demo_duplicate_write_ignore()
            await self.demo_missing_delete_error()
            await self.demo_missing_delete_ignore()
            await self.demo_both_ignore()
            await self.demo_both_error()
            await self.demo_mixed_ignore_duplicate_error_missing()
            await self.demo_mixed_error_duplicate_ignore_missing()

            print("\n" + "=" * 80)
            print("Summary")
            print("=" * 80)
            print("\n✓ All 8 test scenarios completed successfully!")
            print("\nConflict options tested:")
            print("  1. Duplicate writes with ERROR (default)")
            print("  2. Duplicate writes with IGNORE")
            print("  3. Missing deletes with ERROR (default)")
            print("  4. Missing deletes with IGNORE")
            print("  5. Both options set to IGNORE")
            print("  6. Both options set to ERROR")
            print("  7. IGNORE duplicates, ERROR on missing")
            print("  8. ERROR on duplicates, IGNORE missing")
            print("\n" + "=" * 80)

        except Exception as e:
            print(f"\n✗ Error occurred: {type(e).__name__}")
            print(f"   Message: {str(e)}")
            raise
        finally:
            await self.cleanup()


async def main():
    """Main entry point for the demo."""
    # Get API URL from environment or use default
    api_url = os.getenv("FGA_API_URL", "http://localhost:8080")
    
    print("\n" + "=" * 80)
    print("OpenFGA Conflict Options Demonstration")
    print("=" * 80)
    print(f"\nAPI URL: {api_url}")
    print("\nThis demo will test all permutations of conflict options:")
    print("  - on_duplicate_writes: ERROR, IGNORE")
    print("  - on_missing_deletes: ERROR, IGNORE")
    print("\nTotal test scenarios: 8")
    
    demo = ConflictOptionsDemo(api_url=api_url)
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
