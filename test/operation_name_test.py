import unittest
from unittest.mock import Mock, patch
from openfga_sdk.exceptions import ApiException, ValidationException
from openfga_sdk.telemetry.attributes import TelemetryAttributes


class OperationNameExtractionTest(unittest.TestCase):

    def test_operation_name_extracted_from_telemetry(self):
        telemetry_attrs = {
            TelemetryAttributes.fga_client_request_method: "check",
            TelemetryAttributes.fga_client_request_store_id: "store-123"
        }

        operation_name = telemetry_attrs.get(TelemetryAttributes.fga_client_request_method)

        self.assertEqual(operation_name, "check")

    def test_various_operation_names(self):
        operations = ["check", "write", "batch_check", "expand", "read", "list_objects"]

        for op in operations:
            telemetry_attrs = {
                TelemetryAttributes.fga_client_request_method: op
            }

            operation_name = telemetry_attrs.get(TelemetryAttributes.fga_client_request_method)
            self.assertEqual(operation_name, op)

    def test_operation_name_in_exception_message(self):
        e = ValidationException(status=400, reason="Bad Request", operation_name="write")
        error_str = str(e)

        self.assertIn("Operation: write", error_str)

    def test_operation_name_for_different_operations(self):
        operations = [
            ("check", "Check operation"),
            ("write", "Write operation"),
            ("batch_check", "Batch check operation"),
            ("expand", "Expand operation"),
            ("read", "Read operation"),
        ]

        for op_name, description in operations:
            with self.subTest(operation=op_name):
                e = ApiException(status=400, operation_name=op_name)
                self.assertEqual(e.operation_name, op_name)
                error_str = str(e)
                self.assertIn(f"Operation: {op_name}", error_str)


if __name__ == "__main__":
    unittest.main()
