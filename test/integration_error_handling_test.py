import unittest
import asyncio
import time
import os

from openfga_sdk import OpenFgaClient
from openfga_sdk.client.models import ClientConfiguration
from openfga_sdk.exceptions import (
    ApiException,
    ValidationException,
    NotFoundException,
    UnauthorizedException,
)
from openfga_sdk.models import (
    CheckRequest,
    TupleKey,
    WriteRequest,
    WriteRequestWrites,
    ReadRequest,
)


class IntegrationErrorHandlingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_url = os.getenv("OPENFGA_API_URL", "http://localhost:8080")
        cls.config = ClientConfiguration(api_url=api_url)
        cls.client = OpenFgaClient(cls.config)

        cls.wait_for_server(api_url)

        async def create_store():
            response = await cls.client.create_store({"name": "Test Store"})
            return response.id

        cls.store_id = asyncio.run(create_store())
        cls.config.store_id = cls.store_id

        async def create_model():
            model = {
                "type_definitions": [
                    {
                        "type": "user",
                    },
                    {
                        "type": "document",
                        "relations": {
                            "reader": {
                                "this": {},
                            },
                            "writer": {
                                "this": {},
                            },
                        },
                        "metadata": {
                            "relations": {
                                "reader": {"directly_related_user_types": [{"type": "user"}]},
                                "writer": {"directly_related_user_types": [{"type": "user"}]},
                            }
                        },
                    },
                ],
                "schema_version": "1.1",
            }
            response = await cls.client.write_authorization_model(body=model)
            return response.authorization_model_id

        cls.model_id = asyncio.run(create_model())

    @classmethod
    def wait_for_server(cls, api_url, max_retries=30, delay=1):
        import requests
        for i in range(max_retries):
            try:
                response = requests.get(f"{api_url}/healthz")
                if response.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(delay)
        raise Exception(f"Server at {api_url} did not become ready in time")

    @classmethod
    def tearDownClass(cls):
        async def cleanup():
            await cls.client.close()

        asyncio.run(cleanup())

    def test_validation_error_with_improved_properties(self):
        async def run_test():
            try:
                await self.client.check(
                    body=CheckRequest(
                        tuple_key=TupleKey(
                            user="invalid user format",
                            relation="reader",
                            object="document:budget",
                        ),
                        authorization_model_id=self.model_id,
                    )
                )
                self.fail("Expected ValidationException")
            except ApiException as e:
                self.assertIsNotNone(e.code, "Error should have code property")
                self.assertIsNotNone(e.error_message, "Error should have error_message property")
                self.assertIsNotNone(e.request_id, "Error should have request_id property")
                self.assertIsNotNone(e.operation_name, "Error should have operation_name from telemetry")
                self.assertEqual(e.operation_name, "check", "Operation name should be 'check'")

                self.assertTrue(e.is_validation_error(), "Should be identified as validation error")
                self.assertFalse(e.is_not_found_error(), "Should not be identified as not found error")
                self.assertFalse(e.is_server_error(), "Should not be identified as server error")

                error_str = str(e)
                self.assertIn("Operation: check", error_str, "Error string should contain operation name")
                self.assertIn("Status:", error_str, "Error string should contain status")
                self.assertIn("Error Code:", error_str, "Error string should contain error code")
                self.assertIn("Message:", error_str, "Error string should contain message")
                self.assertIn("Request ID:", error_str, "Error string should contain request ID")

                print("\n=== Validation Error Example ===")
                print(f"Direct property access:")
                print(f"  - Operation Name: {e.operation_name}")
                print(f"  - Error Code: {e.code}")
                print(f"  - Message: {e.error_message}")
                print(f"  - Request ID: {e.request_id}")
                print(f"  - Status: {e.status}")
                print(f"\nHelper methods:")
                print(f"  - is_validation_error(): {e.is_validation_error()}")
                print(f"  - is_retryable(): {e.is_retryable()}")
                print(f"\nFormatted error string:\n{error_str}")

        asyncio.run(run_test())

    def test_not_found_error_with_improved_properties(self):
        async def run_test():
            try:
                await self.client.read(
                    body=ReadRequest(
                        tuple_key=TupleKey(
                            user="user:anne",
                            relation="reader",
                            object="document:nonexistent",
                        )
                    )
                )
            except ApiException as e:
                self.assertIsNotNone(e.request_id, "Error should have request_id property")

                self.assertFalse(e.is_validation_error(), "Should not be validation error")
                self.assertFalse(e.is_server_error(), "Should not be server error")

                error_str = str(e)
                self.assertIn("Status:", error_str)
                self.assertIn("Request ID:", error_str)

                print("\n=== Not Found / Read Error Example ===")
                print(f"Direct property access:")
                print(f"  - Request ID: {e.request_id}")
                print(f"  - Status: {e.status}")
                print(f"\nFormatted error string:\n{error_str}")

        asyncio.run(run_test())

    def test_invalid_tuple_validation_error(self):
        async def run_test():
            try:
                await self.client.write(
                    body=WriteRequest(
                        writes=WriteRequestWrites(
                            tuple_keys=[
                                TupleKey(
                                    user="user:anne",
                                    relation="invalid_relation",
                                    object="document:budget",
                                )
                            ]
                        )
                    )
                )
                self.fail("Expected ValidationException")
            except ApiException as e:
                self.assertIsNotNone(e.code)
                self.assertIsNotNone(e.error_message)
                self.assertIsNotNone(e.operation_name)
                self.assertEqual(e.operation_name, "write", "Operation name should be 'write'")
                self.assertTrue(e.is_validation_error())

                print("\n=== Invalid Relation Validation Error ===")
                print(f"Operation: {e.operation_name}")
                print(f"Error Code: {e.code}")
                print(f"Message: {e.error_message}")
                print(f"Request ID: {e.request_id}")
                print(f"\nFormatted:\n{str(e)}")

        asyncio.run(run_test())

    def test_invalid_authorization_model_id(self):
        async def run_test():
            try:
                await self.client.check(
                    body=CheckRequest(
                        tuple_key=TupleKey(
                            user="user:anne",
                            relation="reader",
                            object="document:budget",
                        ),
                        authorization_model_id="01INVALID0MODEL0ID0000000000",
                    )
                )
            except ApiException as e:
                self.assertIsNotNone(e.request_id)

                print("\n=== Invalid Model ID Error ===")
                print(f"Request ID: {e.request_id}")
                print(f"Status: {e.status}")
                if e.code:
                    print(f"Error Code: {e.code}")
                if e.error_message:
                    print(f"Message: {e.error_message}")
                print(f"\nFormatted:\n{str(e)}")

        asyncio.run(run_test())

    def test_helper_methods_comprehensive(self):
        async def run_test():
            try:
                await self.client.check(
                    body=CheckRequest(
                        tuple_key=TupleKey(
                            user="invalid format",
                            relation="reader",
                            object="document:budget",
                        ),
                        authorization_model_id=self.model_id,
                    )
                )
            except ApiException as e:
                print("\n=== Helper Methods Showcase ===")
                print(f"Exception type: {type(e).__name__}")
                print(f"Status code: {e.status}")
                print(f"\nHelper method results:")
                print(f"  - is_validation_error(): {e.is_validation_error()}")
                print(f"  - is_not_found_error(): {e.is_not_found_error()}")
                print(f"  - is_authentication_error(): {e.is_authentication_error()}")
                print(f"  - is_authorization_error(): {e.is_authorization_error()}")
                print(f"  - is_rate_limit_error(): {e.is_rate_limit_error()}")
                print(f"  - is_server_error(): {e.is_server_error()}")
                print(f"  - is_retryable(): {e.is_retryable()}")

        asyncio.run(run_test())

    def test_convenience_vs_old_access_pattern(self):
        async def run_test():
            try:
                await self.client.check(
                    body=CheckRequest(
                        tuple_key=TupleKey(
                            user="bad format",
                            relation="reader",
                            object="document:budget",
                        ),
                        authorization_model_id=self.model_id,
                    )
                )
            except ApiException as e:
                print("\n=== Old vs New Access Patterns ===")
                print("\nOLD WAY (verbose):")
                print(f"  code = e.parsed_exception.code if e.parsed_exception else None")
                print(f"  Result: {e.parsed_exception.code if e.parsed_exception else None}")
                print(f"  message = e.parsed_exception.message if e.parsed_exception else None")
                print(f"  Result: {e.parsed_exception.message if e.parsed_exception else None}")
                print(f"  request_id = e.header.get('fga-request-id')")
                print(f"  Result: {e.header.get('fga-request-id')}")

                print("\nNEW WAY (convenient):")
                print(f"  code = e.code")
                print(f"  Result: {e.code}")
                print(f"  message = e.error_message")
                print(f"  Result: {e.error_message}")
                print(f"  request_id = e.request_id")
                print(f"  Result: {e.request_id}")

                print("\nOLD ERROR STRING:")
                old_style = f"({e.status})\nReason: {e.reason}\nHTTP response body: (would show raw JSON)"

                print("\nNEW ERROR STRING:")
                print(str(e))

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main(verbosity=2)
