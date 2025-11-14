import unittest
from openfga_sdk.exceptions import (
    ApiException,
    ValidationException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ServiceException,
    RateLimitExceededError,
)
from openfga_sdk.models import ValidationErrorMessageResponse, ErrorCode


class ErrorHandlingImprovementsTest(unittest.TestCase):

    def test_operation_name_parameter(self):
        e = ApiException(status=400, reason="Bad Request", operation_name="Check")
        self.assertEqual(e.operation_name, "Check")

        e2 = ValidationException(status=400, operation_name="Write")
        self.assertEqual(e2.operation_name, "Write")

    def test_convenience_properties_with_parsed_exception(self):
        e = ApiException(status=400, reason="Bad Request")

        error_response = ValidationErrorMessageResponse(
            code="validation_error",
            message="Invalid tuple format"
        )
        e.parsed_exception = error_response

        self.assertEqual(e.code, "validation_error")
        self.assertEqual(e.error_message, "Invalid tuple format")

    def test_convenience_properties_without_parsed_exception(self):
        e = ApiException(status=500, reason="Internal Server Error")

        self.assertIsNone(e.code)
        self.assertIsNone(e.error_message)

    def test_request_id_property(self):
        e = ApiException(status=400, reason="Bad Request")
        e.header["fga-request-id"] = "test-request-id-123"

        self.assertEqual(e.request_id, "test-request-id-123")

    def test_store_id_property(self):
        e = ApiException(status=400, reason="Bad Request")
        e.header["store_id"] = "store-123"

        self.assertEqual(e.store_id, "store-123")

    def test_authorization_model_id_property(self):
        e = ApiException(status=400, reason="Bad Request")
        e.header["openfga_authorization_model_id"] = "model-456"

        self.assertEqual(e.authorization_model_id, "model-456")

    def test_is_validation_error(self):
        e1 = ValidationException(status=400)
        self.assertTrue(e1.is_validation_error())

        e2 = ApiException(status=400)
        error_response = ValidationErrorMessageResponse(
            code="validation_error",
            message="test"
        )
        e2.parsed_exception = error_response
        self.assertTrue(e2.is_validation_error())

        e3 = NotFoundException(status=404)
        self.assertFalse(e3.is_validation_error())

    def test_is_not_found_error(self):
        e1 = NotFoundException(status=404)
        self.assertTrue(e1.is_not_found_error())

        e2 = ApiException(status=404)
        self.assertTrue(e2.is_not_found_error())

        e3 = ValidationException(status=400)
        self.assertFalse(e3.is_not_found_error())

    def test_is_authentication_error(self):
        e1 = UnauthorizedException(status=401)
        self.assertTrue(e1.is_authentication_error())

        e2 = ApiException(status=401)
        self.assertTrue(e2.is_authentication_error())

        e3 = ValidationException(status=400)
        self.assertFalse(e3.is_authentication_error())

    def test_is_authorization_error(self):
        e1 = ForbiddenException(status=403)
        self.assertTrue(e1.is_authorization_error())

        e2 = ApiException(status=403)
        self.assertTrue(e2.is_authorization_error())

        e3 = ValidationException(status=400)
        self.assertFalse(e3.is_authorization_error())

    def test_is_rate_limit_error(self):
        e1 = RateLimitExceededError(status=429)
        self.assertTrue(e1.is_rate_limit_error())

        e2 = ApiException(status=429)
        self.assertTrue(e2.is_rate_limit_error())

        e3 = ValidationException(status=400)
        self.assertFalse(e3.is_rate_limit_error())

    def test_is_server_error(self):
        e1 = ServiceException(status=500)
        self.assertTrue(e1.is_server_error())

        e2 = ApiException(status=502)
        self.assertTrue(e2.is_server_error())

        e3 = ApiException(status=503)
        self.assertTrue(e3.is_server_error())

        e4 = ValidationException(status=400)
        self.assertFalse(e4.is_server_error())

    def test_is_retryable(self):
        retryable_codes = [429, 500, 502, 503, 504]
        for code in retryable_codes:
            e = ApiException(status=code)
            self.assertTrue(e.is_retryable(), f"Status {code} should be retryable")

        non_retryable_codes = [400, 401, 403, 404]
        for code in non_retryable_codes:
            e = ApiException(status=code)
            self.assertFalse(e.is_retryable(), f"Status {code} should not be retryable")

    def test_enhanced_str_with_operation_name(self):
        e = ApiException(status=400, reason="Bad Request", operation_name="Check")
        error_str = str(e)

        self.assertIn("Operation: Check", error_str)
        self.assertIn("Status: 400", error_str)

    def test_enhanced_str_with_all_fields(self):
        e = ApiException(status=400, reason="Bad Request", operation_name="Write")

        error_response = ValidationErrorMessageResponse(
            code="validation_error",
            message="Invalid tuple"
        )
        e.parsed_exception = error_response
        e.header["fga-request-id"] = "req-123"
        e.header["store_id"] = "store-456"
        e.header["openfga_authorization_model_id"] = "model-789"

        error_str = str(e)

        self.assertIn("Operation: Write", error_str)
        self.assertIn("Status: 400", error_str)
        self.assertIn("Error Code: validation_error", error_str)
        self.assertIn("Message: Invalid tuple", error_str)
        self.assertIn("Request ID: req-123", error_str)
        self.assertIn("Store ID: store-456", error_str)
        self.assertIn("Authorization Model ID: model-789", error_str)

    def test_enhanced_str_without_operation_name(self):
        e = ApiException(status=400, reason="Bad Request")
        error_str = str(e)

        self.assertNotIn("Operation:", error_str)
        self.assertIn("Status: 400", error_str)

    def test_backwards_compatibility_with_parsed_exception(self):
        e = ApiException(status=400, reason="Bad Request")

        error_response = ValidationErrorMessageResponse(
            code="validation_error",
            message="Test error"
        )
        e.parsed_exception = error_response

        self.assertEqual(e.code, "validation_error")
        self.assertEqual(e.error_message, "Test error")


if __name__ == "__main__":
    unittest.main()
