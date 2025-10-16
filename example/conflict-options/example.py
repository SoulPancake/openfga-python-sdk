# ruff: noqa: E402

"""
Python SDK for OpenFGA - Conflict Options Example

This example demonstrates the on_duplicate and on_missing conflict options
for write operations introduced in OpenFGA v1.10.0.

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)
"""

import asyncio
import json
import os
import sys


###
# The following two lines are just a convenience for SDK development and testing,
# and should not be used in your code. They allow you to run this example using the
# local SDK code from the parent directory, rather than using the installed package.
###
sdk_path = os.path.realpath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sys.path.insert(0, sdk_path)

from openfga_sdk.client import OpenFgaClient
from openfga_sdk.client.configuration import ClientConfiguration
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_conflict_opts import (
    ClientWriteRequestOnDuplicateWrites,
    ClientWriteRequestOnMissingDeletes,
    ConflictOptions,
)
from openfga_sdk.client.models.write_request import ClientWriteRequest
from openfga_sdk.exceptions import FgaValidationException
from openfga_sdk.models.create_store_request import CreateStoreRequest


async def create_store(openfga: OpenFgaClient) -> str:
    """
    Create a temporary store for testing.
    """
    response = await openfga.create_store(CreateStoreRequest(name="Conflict Options Demo Store"))
    return response.id


async def write_model(openfga: OpenFgaClient) -> str:
    """
    Load the authorization model from a file and write it to the server.
    """
    with open("model.json") as model:
        response = await openfga.write_authorization_model(json.loads(model.read()))
        return response.authorization_model_id


def print_checkpoint(title: str, description: str = ""):
    """
    Print a checkpoint marker for readability.
    """
    print("\n" + "=" * 80)
    print(f"CHECKPOINT: {title}")
    if description:
        print(f"{description}")
    print("=" * 80 + "\n")


async def demonstrate_duplicate_writes_error(openfga: OpenFgaClient):
    """
    Demonstrate the default behavior when writing duplicate tuples (ERROR mode).
    """
    print_checkpoint(
        "1. Duplicate Writes - ERROR Mode (Default)",
        "Writing a tuple twice without conflict options will result in an error."
    )

    tuple_to_write = ClientTuple(
        user="user:alice",
        relation="viewer",
        object="document:roadmap",
    )

    # First write - should succeed
    print("✓ Writing tuple for the first time...")
    await openfga.write_tuples([tuple_to_write])
    print(f"  Successfully wrote: {tuple_to_write.user} is {tuple_to_write.relation} of {tuple_to_write.object}")

    # Second write - should fail with default behavior
    print("\n✗ Attempting to write the same tuple again (expecting error)...")
    try:
        await openfga.write_tuples([tuple_to_write])
        print("  ERROR: Should have failed but didn't!")
    except FgaValidationException as e:
        print(f"  Expected error occurred: {type(e).__name__}")
        print(f"  This is the default behavior when writing duplicate tuples.")


async def demonstrate_duplicate_writes_ignore(openfga: OpenFgaClient):
    """
    Demonstrate ignoring duplicate writes using on_duplicate=IGNORE.
    """
    print_checkpoint(
        "2. Duplicate Writes - IGNORE Mode",
        "Using on_duplicate=IGNORE will treat duplicate writes as no-ops."
    )

    tuple_to_write = ClientTuple(
        user="user:bob",
        relation="editor",
        object="document:budget",
    )

    # Write with IGNORE conflict option
    print("✓ Writing tuple with on_duplicate=IGNORE...")
    options = {
        "conflict": ConflictOptions(
            on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE
        )
    }

    # First write
    await openfga.write_tuples([tuple_to_write], options)
    print(f"  Successfully wrote: {tuple_to_write.user} is {tuple_to_write.relation} of {tuple_to_write.object}")

    # Second write - should succeed silently (no-op)
    print("\n✓ Writing the same tuple again with on_duplicate=IGNORE...")
    await openfga.write_tuples([tuple_to_write], options)
    print("  Success! The duplicate write was silently ignored (no error thrown).")


async def demonstrate_missing_deletes_error(openfga: OpenFgaClient):
    """
    Demonstrate the default behavior when deleting non-existent tuples (ERROR mode).
    """
    print_checkpoint(
        "3. Missing Deletes - ERROR Mode (Default)",
        "Deleting a tuple that doesn't exist will result in an error by default."
    )

    tuple_to_delete = ClientTuple(
        user="user:charlie",
        relation="owner",
        object="document:nonexistent",
    )

    print("✗ Attempting to delete a non-existent tuple (expecting error)...")
    try:
        await openfga.delete_tuples([tuple_to_delete])
        print("  ERROR: Should have failed but didn't!")
    except FgaValidationException as e:
        print(f"  Expected error occurred: {type(e).__name__}")
        print(f"  This is the default behavior when deleting non-existent tuples.")


async def demonstrate_missing_deletes_ignore(openfga: OpenFgaClient):
    """
    Demonstrate ignoring missing deletes using on_missing=IGNORE.
    """
    print_checkpoint(
        "4. Missing Deletes - IGNORE Mode",
        "Using on_missing=IGNORE will treat deletes of non-existent tuples as no-ops."
    )

    tuple_to_delete = ClientTuple(
        user="user:diana",
        relation="viewer",
        object="document:imaginary",
    )

    print("✓ Attempting to delete a non-existent tuple with on_missing=IGNORE...")
    options = {
        "conflict": ConflictOptions(
            on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE
        )
    }

    await openfga.delete_tuples([tuple_to_delete], options)
    print("  Success! The delete of non-existent tuple was silently ignored (no error thrown).")


async def demonstrate_combined_conflict_options(openfga: OpenFgaClient):
    """
    Demonstrate using both conflict options together.
    """
    print_checkpoint(
        "5. Combined Conflict Options",
        "Both on_duplicate and on_missing can be used together in a single write operation."
    )

    write_tuple = ClientTuple(
        user="user:eve",
        relation="viewer",
        object="document:combined",
    )

    delete_tuple = ClientTuple(
        user="user:frank",
        relation="editor",
        object="document:doesnotexist",
    )

    options = {
        "conflict": ConflictOptions(
            on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
            on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
        )
    }

    print("✓ Performing a mixed write operation with both conflict options...")
    print(f"  - Writing (may be duplicate): {write_tuple.user} is {write_tuple.relation} of {write_tuple.object}")
    print(f"  - Deleting (may not exist): {delete_tuple.user} is {delete_tuple.relation} of {delete_tuple.object}")

    # First write
    await openfga.write(
        ClientWriteRequest(writes=[write_tuple], deletes=[delete_tuple]),
        options
    )
    print("\n  Success! First operation completed.")

    # Second write with same tuples (duplicate write, missing delete)
    print("\n✓ Performing the same operation again (duplicate write + missing delete)...")
    await openfga.write(
        ClientWriteRequest(writes=[write_tuple], deletes=[delete_tuple]),
        options
    )
    print("  Success! Both operations were silently ignored (no errors thrown).")


async def demonstrate_explicit_error_mode(openfga: OpenFgaClient):
    """
    Demonstrate explicitly setting ERROR mode for both options.
    """
    print_checkpoint(
        "6. Explicit ERROR Mode",
        "You can explicitly set ERROR mode if you want to be explicit about the behavior."
    )

    tuple_to_write = ClientTuple(
        user="user:george",
        relation="viewer",
        object="document:explicit",
    )

    options = {
        "conflict": ConflictOptions(
            on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.ERROR,
            on_missing_deletes=ClientWriteRequestOnMissingDeletes.ERROR,
        )
    }

    print("✓ Writing tuple with explicit on_duplicate=ERROR...")
    await openfga.write_tuples([tuple_to_write], options)
    print(f"  Successfully wrote: {tuple_to_write.user} is {tuple_to_write.relation} of {tuple_to_write.object}")

    print("\n✗ Attempting to write the same tuple again with on_duplicate=ERROR...")
    try:
        await openfga.write_tuples([tuple_to_write], options)
        print("  ERROR: Should have failed but didn't!")
    except FgaValidationException as e:
        print(f"  Expected error occurred: {type(e).__name__}")
        print(f"  This demonstrates that ERROR mode is the default behavior.")


async def main():
    """
    Main function to run all demonstrations.
    """
    print("\n" + "=" * 80)
    print("OpenFGA Python SDK - Conflict Options Example")
    print("=" * 80)
    print("\nThis example demonstrates the on_duplicate and on_missing conflict options")
    print("for write operations introduced in OpenFGA v1.10.0.")
    print("\nRequirements:")
    print("  - OpenFGA server v1.10.0 or later running on localhost:8080")
    print("  - The server must support conflict options in write operations")

    configure = ClientConfiguration(
        api_url="http://localhost:8080",
    )

    async with OpenFgaClient(configure) as openfga:
        # Create temporary store
        print_checkpoint("Setup", "Creating temporary store and authorization model...")
        store = await create_store(openfga)
        print(f"✓ Created temporary store: {store}")

        # Configure the SDK to use the temporary store
        openfga.set_store_id(store)

        # Load and write the authorization model
        model = await write_model(openfga)
        print(f"✓ Created authorization model: {model}")
        openfga.set_authorization_model_id(model)

        # Run all demonstrations
        try:
            await demonstrate_duplicate_writes_error(openfga)
            await demonstrate_duplicate_writes_ignore(openfga)
            await demonstrate_missing_deletes_error(openfga)
            await demonstrate_missing_deletes_ignore(openfga)
            await demonstrate_combined_conflict_options(openfga)
            await demonstrate_explicit_error_mode(openfga)

            print_checkpoint(
                "Summary",
                "All demonstrations completed successfully!"
            )

            print("Key Takeaways:")
            print("  1. on_duplicate controls behavior when writing tuples that already exist")
            print("     - ERROR (default): Returns an error")
            print("     - IGNORE: Treats as no-op, no error thrown")
            print("")
            print("  2. on_missing controls behavior when deleting tuples that don't exist")
            print("     - ERROR (default): Returns an error")
            print("     - IGNORE: Treats as no-op, no error thrown")
            print("")
            print("  3. Both options can be used together in a single write operation")
            print("  4. These options are available in OpenFGA v1.10.0 and later")

        finally:
            # Clean up
            print_checkpoint("Cleanup", "Deleting temporary store...")
            await openfga.delete_store()
            print(f"✓ Deleted temporary store: {store}")

    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
