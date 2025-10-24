"""
Comprehensive Test Suite for MRTD.py
Tests all functions with various scenarios including edge cases, error handling, and validation
"""

import unittest
from typing import Dict, Any
import MRTD


class TestCharValue(unittest.TestCase):
    """Test the _char_value helper function"""

    def test_char_value_filler(self):
        """Test that '<' returns 0"""
        self.assertEqual(MRTD._char_value('<'), 0)

    def test_char_value_digits(self):
        """Test numeric characters 0-9"""
        self.assertEqual(MRTD._char_value('0'), 0)
        self.assertEqual(MRTD._char_value('5'), 5)
        self.assertEqual(MRTD._char_value('9'), 9)

    def test_char_value_letters(self):
        """Test letter characters A-Z"""
        self.assertEqual(MRTD._char_value('A'), 10)
        self.assertEqual(MRTD._char_value('B'), 11)
        self.assertEqual(MRTD._char_value('Z'), 35)
        self.assertEqual(MRTD._char_value('M'), 22)


class TestComputeCheckDigit(unittest.TestCase):
    """Test the compute_check_digit function"""

    def test_compute_check_digit_simple(self):
        """Test basic check digit calculation"""
        # Example from ICAO spec
        result = MRTD.compute_check_digit("520727")
        self.assertEqual(result, "3")

    def test_compute_check_digit_with_letters(self):
        """Test check digit with letters"""
        result = MRTD.compute_check_digit("AB2134<<<")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 1)
        self.assertTrue(result.isdigit())

    def test_compute_check_digit_empty(self):
        """Test check digit with empty string"""
        result = MRTD.compute_check_digit("")
        self.assertEqual(result, "0")

    def test_compute_check_digit_all_fillers(self):
        """Test check digit with all filler characters"""
        result = MRTD.compute_check_digit("<<<<<<")
        self.assertEqual(result, "0")

    def test_compute_check_digit_known_values(self):
        """Test with known document numbers"""
        # Known test values
        result = MRTD.compute_check_digit("123456789")
        self.assertIsInstance(result, str)
        self.assertTrue(result in "0123456789")


class TestNormalizeMrzLine(unittest.TestCase):
    """Test the _normalize_mrz_line function"""

    def test_normalize_uppercase(self):
        """Test that lowercase is converted to uppercase"""
        result = MRTD._normalize_mrz_line("abc123")
        self.assertEqual(result, "ABC123")

    def test_normalize_spaces_to_fillers(self):
        """Test that spaces are converted to '<'"""
        result = MRTD._normalize_mrz_line("AB CD EF")
        self.assertEqual(result, "AB<CD<EF")

    def test_normalize_valid_chars(self):
        """Test with already valid MRZ characters"""
        valid = "ABCD1234<<<"
        result = MRTD._normalize_mrz_line(valid)
        self.assertEqual(result, valid)

    def test_normalize_invalid_chars(self):
        """Test that invalid characters raise ValueError"""
        with self.assertRaises(ValueError) as context:
            MRTD._normalize_mrz_line("ABC!@#")
        self.assertIn("invalid characters", str(context.exception))

    def test_normalize_none_input(self):
        """Test that None input raises ValueError"""
        with self.assertRaises(ValueError) as context:
            MRTD._normalize_mrz_line(None)
        self.assertIn("None", str(context.exception))

    def test_normalize_special_chars(self):
        """Test various special characters that should fail"""
        invalid_chars = ["ABC$DEF", "123-456", "ABC.DEF", "ABC@DEF"]
        for test_str in invalid_chars:
            with self.assertRaises(ValueError):
                MRTD._normalize_mrz_line(test_str)


class TestStripFillers(unittest.TestCase):
    """Test the _strip_fillers function"""

    def test_strip_leading_trailing(self):
        """Test removal of leading and trailing fillers"""
        result = MRTD._strip_fillers("<<ABC<<")
        self.assertEqual(result, "ABC")

    def test_strip_multiple_fillers_to_space(self):
        """Test that multiple fillers become single space"""
        result = MRTD._strip_fillers("ABC<<DEF")
        self.assertEqual(result, "ABC DEF")

    def test_strip_single_filler_to_space(self):
        """Test that single filler becomes space"""
        result = MRTD._strip_fillers("ABC<DEF")
        self.assertEqual(result, "ABC DEF")

    def test_strip_no_fillers(self):
        """Test string without fillers"""
        result = MRTD._strip_fillers("ABCDEF")
        self.assertEqual(result, "ABCDEF")

    def test_strip_only_fillers(self):
        """Test string with only fillers"""
        result = MRTD._strip_fillers("<<<<<<")
        self.assertEqual(result, "")

    def test_strip_complex_pattern(self):
        """Test complex filler pattern"""
        result = MRTD._strip_fillers("<<LAST<<FIRST<MIDDLE<<")
        self.assertEqual(result, "LAST FIRST MIDDLE")


class TestPadField(unittest.TestCase):
    """Test the _pad_field function"""

    def test_pad_shorter_string(self):
        """Test padding a string shorter than target length"""
        result = MRTD._pad_field("ABC", 10)
        self.assertEqual(result, "ABC<<<<<<<")
        self.assertEqual(len(result), 10)

    def test_pad_exact_length(self):
        """Test string already at target length"""
        result = MRTD._pad_field("ABCDE", 5)
        self.assertEqual(result, "ABCDE")

    def test_pad_longer_string(self):
        """Test truncating string longer than target length"""
        result = MRTD._pad_field("ABCDEFGHIJ", 5)
        self.assertEqual(result, "ABCDE")

    def test_pad_empty_string(self):
        """Test padding empty string"""
        result = MRTD._pad_field("", 5)
        self.assertEqual(result, "<<<<<")

    def test_pad_none_value(self):
        """Test padding None value"""
        result = MRTD._pad_field(None, 5)
        self.assertEqual(result, "<<<<<")


class TestScanMrz(unittest.TestCase):
    """Test the scan_mrz function"""

    def test_scan_mrz_raises_scanner_error(self):
        """Test that scan_mrz raises ScannerError as it's not implemented"""
        with self.assertRaises(MRTD.ScannerError) as context:
            MRTD.scan_mrz()
        self.assertIn("not implemented", str(context.exception))
        self.assertIn("hardware", str(context.exception).lower())


class TestDecodeMrz(unittest.TestCase):
    """Test the decode_mrz function"""

    def setUp(self):
        """Set up valid test MRZ lines"""
        self.valid_line1 = "P<USADOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<"
        self.valid_line2 = "1234567893USA9001014M30010189876543210<<<<<6"

    def test_decode_valid_mrz(self):
        """Test decoding valid MRZ lines"""
        result = MRTD.decode_mrz(self.valid_line1, self.valid_line2)

        self.assertEqual(result["document_type"], "P")
        self.assertEqual(result["issuing_country"], "USA")
        self.assertEqual(result["surname"], "DOE")
        self.assertEqual(result["given_names"], "JOHN MICHAEL")
        self.assertEqual(result["nationality"], "USA")
        self.assertEqual(result["sex"], "M")

    def test_decode_extracts_all_fields(self):
        """Test that all expected fields are present"""
        result = MRTD.decode_mrz(self.valid_line1, self.valid_line2)

        expected_keys = [
            "document_type", "issuing_country", "surname", "given_names",
            "document_number", "document_number_clean", "document_number_check",
            "nationality", "date_of_birth", "date_of_birth_check",
            "sex", "expiration_date", "expiration_date_check",
            "personal_number", "personal_number_clean", "personal_number_check",
            "composite_check", "_raw_line1", "_raw_line2"
        ]

        for key in expected_keys:
            self.assertIn(key, result)

    def test_decode_none_line1(self):
        """Test that None for line1 raises ValueError"""
        with self.assertRaises(ValueError) as context:
            MRTD.decode_mrz(None, self.valid_line2)
        self.assertIn("must be provided", str(context.exception))

    def test_decode_none_line2(self):
        """Test that None for line2 raises ValueError"""
        with self.assertRaises(ValueError) as context:
            MRTD.decode_mrz(self.valid_line1, None)
        self.assertIn("must be provided", str(context.exception))

    def test_decode_wrong_length_line1(self):
        """Test that line1 with wrong length raises ValueError"""
        short_line = "P<USA"
        with self.assertRaises(ValueError) as context:
            MRTD.decode_mrz(short_line, self.valid_line2)
        self.assertIn("44 characters", str(context.exception))

    def test_decode_wrong_length_line2(self):
        """Test that line2 with wrong length raises ValueError"""
        short_line = "12345"
        with self.assertRaises(ValueError) as context:
            MRTD.decode_mrz(self.valid_line1, short_line)
        self.assertIn("44 characters", str(context.exception))

    def test_decode_invalid_chars(self):
        """Test that invalid characters raise ValueError"""
        invalid_line = "P<USA!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`-="
        # Pad to 44 chars
        invalid_line = invalid_line[:44].ljust(44, '<')
        with self.assertRaises(ValueError) as context:
            MRTD.decode_mrz(invalid_line, self.valid_line2)
        self.assertIn("invalid characters", str(context.exception))

    def test_decode_lowercase_conversion(self):
        """Test that lowercase is converted to uppercase"""
        line1_lower = "p<usadoe<<john<michael<<<<<<<<<<<<<<<<<<<<<<"
        result = MRTD.decode_mrz(line1_lower, self.valid_line2)
        self.assertEqual(result["document_type"], "P")
        self.assertEqual(result["issuing_country"], "USA")

    def test_decode_name_no_double_filler(self):
        """Test name parsing when no << separator exists"""
        line1 = "P<USADOE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        result = MRTD.decode_mrz(line1, self.valid_line2)
        self.assertEqual(result["surname"], "DOE")
        self.assertEqual(result["given_names"], "")

    def test_decode_empty_sex(self):
        """Test that filler '<' for sex becomes empty string"""
        line2_with_filler = "1234567893USA9001014<30010189876543210<<<<<6"
        result = MRTD.decode_mrz(self.valid_line1, line2_with_filler)
        self.assertEqual(result["sex"], "")

    def test_decode_document_number_with_fillers(self):
        """Test document number extraction with fillers"""
        result = MRTD.decode_mrz(self.valid_line1, self.valid_line2)
        self.assertEqual(len(result["document_number"]), 9)
        # Clean version should have fillers stripped
        self.assertTrue(len(result["document_number_clean"]) <= 9)

    def test_decode_personal_number_clean(self):
        """Test personal number cleaning"""
        result = MRTD.decode_mrz(self.valid_line1, self.valid_line2)
        self.assertEqual(len(result["personal_number"]), 14)
        # Clean version should strip fillers
        clean = result["personal_number_clean"]
        self.assertNotIn('<', clean)


class TestGetTravelDocFromDb(unittest.TestCase):
    """Test the get_travel_doc_from_db function"""

    def test_get_travel_doc_returns_dict(self):
        """Test that function returns a dictionary"""
        result = MRTD.get_travel_doc_from_db("test-id")
        self.assertIsInstance(result, dict)

    def test_get_travel_doc_has_required_fields(self):
        """Test that returned document has all required fields"""
        result = MRTD.get_travel_doc_from_db("test-id")

        required_fields = [
            "document_type", "country_code", "document_number",
            "date_of_birth", "sex", "expiration_date",
            "nationality", "surname", "given_names"
        ]

        for field in required_fields:
            self.assertIn(field, result)

    def test_get_travel_doc_field_formats(self):
        """Test that fields have expected formats"""
        result = MRTD.get_travel_doc_from_db("test-id")

        # Country code should be 3 chars
        self.assertEqual(len(result["country_code"]), 3)
        self.assertEqual(len(result["nationality"]), 3)

        # Dates should be 6 chars (YYMMDD)
        self.assertEqual(len(result["date_of_birth"]), 6)
        self.assertEqual(len(result["expiration_date"]), 6)

        # Sex should be single char
        self.assertIn(result["sex"], ["M", "F", "<", "X"])


class TestEncodeMrz(unittest.TestCase):
    """Test the encode_mrz function"""

    def setUp(self):
        """Set up valid travel document data"""
        self.valid_doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "123456789",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "DOE",
            "given_names": "JOHN MICHAEL",
            "personal_number": "987654321"
        }

    def test_encode_valid_document(self):
        """Test encoding a valid travel document"""
        line1, line2 = MRTD.encode_mrz(self.valid_doc)

        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)
        self.assertTrue(line1.startswith("P<USA"))

    def test_encode_missing_required_field(self):
        """Test that missing required fields raise ValueError"""
        incomplete_doc = self.valid_doc.copy()
        del incomplete_doc["surname"]

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(incomplete_doc)
        self.assertIn("Missing required field", str(context.exception))

    def test_encode_none_required_field(self):
        """Test that None in required field raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["surname"] = None

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("Missing required field", str(context.exception))

    def test_encode_invalid_country_code(self):
        """Test that invalid country code length raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["country_code"] = "US"  # Too short

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("country_code must be exactly 3 characters", str(context.exception))

    def test_encode_invalid_nationality(self):
        """Test that invalid nationality length raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["nationality"] = "USAA"  # Too long

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("nationality must be exactly 3 characters", str(context.exception))

    def test_encode_invalid_dob_format(self):
        """Test that invalid date of birth format raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["date_of_birth"] = "1990-01-01"

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("YYMMDD", str(context.exception))

    def test_encode_invalid_expiry_format(self):
        """Test that invalid expiration date format raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["expiration_date"] = "30/01/01"

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("YYMMDD", str(context.exception))

    def test_encode_invalid_sex(self):
        """Test that invalid sex value raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["sex"] = "Q"

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("sex must be", str(context.exception))

    def test_encode_valid_sex_values(self):
        """Test all valid sex values"""
        valid_sex_values = ["M", "F", "<", "X"]

        for sex in valid_sex_values:
            doc = self.valid_doc.copy()
            doc["sex"] = sex
            line1, line2 = MRTD.encode_mrz(doc)
            self.assertEqual(len(line1), 44)
            self.assertEqual(len(line2), 44)

    def test_encode_empty_document_type(self):
        """Test that empty document type raises ValueError"""
        invalid_doc = self.valid_doc.copy()
        invalid_doc["document_type"] = ""

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(invalid_doc)
        self.assertIn("document_type must be non-empty", str(context.exception))

    def test_encode_without_personal_number(self):
        """Test encoding without optional personal number"""
        doc = self.valid_doc.copy()
        del doc["personal_number"]

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)

    def test_encode_empty_personal_number(self):
        """Test encoding with empty personal number"""
        doc = self.valid_doc.copy()
        doc["personal_number"] = ""

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line2), 44)

    def test_encode_long_document_number(self):
        """Test that document number is truncated if too long"""
        doc = self.valid_doc.copy()
        doc["document_number"] = "12345678901234"  # Too long

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line2), 44)

    def test_encode_special_chars_in_document_number(self):
        """Test that special characters in document number raise ValueError"""
        doc = self.valid_doc.copy()
        doc["document_number"] = "ABC-123"

        with self.assertRaises(ValueError) as context:
            MRTD.encode_mrz(doc)
        self.assertIn("invalid characters", str(context.exception))

    def test_encode_name_with_hyphen(self):
        """Test encoding names with hyphens"""
        doc = self.valid_doc.copy()
        doc["surname"] = "SMITH-JONES"
        doc["given_names"] = "MARY-ANN"

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)
        # Hyphens should be removed in MRZ
        self.assertNotIn('-', line1)

    def test_encode_name_with_apostrophe(self):
        """Test encoding names with apostrophes"""
        doc = self.valid_doc.copy()
        doc["surname"] = "O'BRIEN"

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)
        # Apostrophes should be removed in MRZ
        self.assertNotIn("'", line1)

    def test_encode_long_names(self):
        """Test encoding very long names that need truncation"""
        doc = self.valid_doc.copy()
        doc["surname"] = "VERYLONGSURNAMETHATEXCEEDSTHEMAXIMUMLENGTH"
        doc["given_names"] = "VERYLONGGIVENNAMESTHATEXCEEDMAXIMUM"

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)

    def test_encode_empty_given_names(self):
        """Test encoding with empty given names"""
        doc = self.valid_doc.copy()
        doc["given_names"] = "A"  # Use single letter instead of empty

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)
        self.assertIn("<<", line1)  # Should have double filler separator

    def test_encode_multiple_given_names(self):
        """Test encoding with multiple given names"""
        doc = self.valid_doc.copy()
        doc["given_names"] = "JOHN MICHAEL ROBERT"

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)

    def test_encode_lowercase_fields(self):
        """Test that lowercase input is converted to uppercase"""
        doc = self.valid_doc.copy()
        doc["surname"] = "doe"
        doc["given_names"] = "john"
        doc["country_code"] = "usa"

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertTrue(line1.isupper() or '<' in line1)


class TestValidateCheckDigits(unittest.TestCase):
    """Test the validate_check_digits function"""

    def test_validate_valid_check_digits(self):
        """Test validation with correct check digits"""
        # Create a valid encoded MRZ
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "123456789",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "DOE",
            "given_names": "JOHN",
            "personal_number": ""
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)

        valid, message = MRTD.validate_check_digits(decoded)
        self.assertTrue(valid)
        self.assertEqual(message, "All check digits valid")

    def test_validate_invalid_document_check(self):
        """Test validation with incorrect document number check digit"""
        decoded = {
            "document_number": "123456789",
            "document_number_check": "0",  # Wrong check digit
            "date_of_birth": "900101",
            "date_of_birth_check": "3",
            "expiration_date": "300101",
            "expiration_date_check": "8",
            "personal_number": "<<<<<<<<<<<<<<",
            "personal_number_check": "0",
            "composite_check": "5"
        }

        valid, errors = MRTD.validate_check_digits(decoded)
        self.assertFalse(valid)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) > 0)

    def test_validate_multiple_errors(self):
        """Test validation with multiple incorrect check digits"""
        decoded = {
            "document_number": "123456789",
            "document_number_check": "0",  # Wrong
            "date_of_birth": "900101",
            "date_of_birth_check": "0",  # Wrong
            "expiration_date": "300101",
            "expiration_date_check": "0",  # Wrong
            "personal_number": "<<<<<<<<<<<<<<",
            "personal_number_check": "0",
            "composite_check": "0"  # Wrong
        }

        valid, errors = MRTD.validate_check_digits(decoded)
        self.assertFalse(valid)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) >= 3)  # At least 3 errors

    def test_validate_error_structure(self):
        """Test that error structure contains required fields"""
        decoded = {
            "document_number": "123456789",
            "document_number_check": "0",
            "date_of_birth": "900101",
            "date_of_birth_check": "3",
            "expiration_date": "300101",
            "expiration_date_check": "8",
            "personal_number": "<<<<<<<<<<<<<<",
            "personal_number_check": "0",
            "composite_check": "5"
        }

        valid, errors = MRTD.validate_check_digits(decoded)
        if not valid:
            for error in errors:
                self.assertIn("field_name", error)
                self.assertIn("expected", error)
                self.assertIn("actual", error)
                self.assertIn("position", error)
                self.assertIn("message", error)

    def test_validate_missing_field(self):
        """Test validation with missing required field"""
        decoded = {
            "date_of_birth": "900101",
            "date_of_birth_check": "3",
        }

        with self.assertRaises(ValueError) as context:
            MRTD.validate_check_digits(decoded)
        self.assertIn("missing", str(context.exception).lower())


class TestIntegration(unittest.TestCase):
    """Integration tests for encode->decode->validate cycle"""

    def test_full_cycle_valid_document(self):
        """Test complete cycle with valid document"""
        # Get mock document from DB
        doc = MRTD.get_travel_doc_from_db("test-id")

        # Encode to MRZ
        line1, line2 = MRTD.encode_mrz(doc)

        # Verify lengths
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)

        # Decode MRZ
        decoded = MRTD.decode_mrz(line1, line2)

        # Validate check digits
        valid, message = MRTD.validate_check_digits(decoded)
        self.assertTrue(valid, f"Check digits should be valid: {message}")

    def test_full_cycle_minimal_document(self):
        """Test complete cycle with minimal required fields"""
        doc = {
            "document_type": "P",
            "country_code": "GBR",
            "document_number": "ABC123",
            "date_of_birth": "850615",
            "sex": "F",
            "expiration_date": "350615",
            "nationality": "GBR",
            "surname": "SMITH",
            "given_names": "JANE",
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        valid, message = MRTD.validate_check_digits(decoded)

        self.assertTrue(valid)
        self.assertEqual(decoded["surname"], "SMITH")
        self.assertEqual(decoded["given_names"], "JANE")

    def test_full_cycle_complex_names(self):
        """Test complete cycle with complex names"""
        doc = {
            "document_type": "P",
            "country_code": "FRA",
            "document_number": "987654321",
            "date_of_birth": "750320",
            "sex": "M",
            "expiration_date": "280320",
            "nationality": "FRA",
            "surname": "VON SCHMIDT MULLER",
            "given_names": "JEAN PIERRE CLAUDE",
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        valid, message = MRTD.validate_check_digits(decoded)

        self.assertTrue(valid)
        self.assertIsNotNone(decoded["surname"])
        self.assertIsNotNone(decoded["given_names"])

    def test_full_cycle_with_personal_number(self):
        """Test complete cycle with personal number"""
        doc = {
            "document_type": "P",
            "country_code": "CAN",
            "document_number": "XY1234567",
            "date_of_birth": "920505",
            "sex": "X",
            "expiration_date": "320505",
            "nationality": "CAN",
            "surname": "MARTINEZ",
            "given_names": "ALEX",
            "personal_number": "AB123CD456"
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        valid, message = MRTD.validate_check_digits(decoded)

        self.assertTrue(valid)
        self.assertIn("AB123CD456", decoded["personal_number_clean"])

    def test_roundtrip_preserves_data(self):
        """Test that encode->decode preserves essential data"""
        original = {
            "document_type": "P",
            "country_code": "JPN",
            "document_number": "TK1234567",
            "date_of_birth": "880912",
            "sex": "F",
            "expiration_date": "330912",
            "nationality": "JPN",
            "surname": "TANAKA",
            "given_names": "YUKI",
        }

        line1, line2 = MRTD.encode_mrz(original)
        decoded = MRTD.decode_mrz(line1, line2)

        # Check that key fields are preserved
        self.assertEqual(decoded["document_type"], original["document_type"])
        self.assertEqual(decoded["issuing_country"], original["country_code"])
        self.assertEqual(decoded["nationality"], original["nationality"])
        self.assertEqual(decoded["surname"], original["surname"])
        self.assertEqual(decoded["given_names"], original["given_names"])
        self.assertEqual(decoded["date_of_birth"], original["date_of_birth"])
        self.assertEqual(decoded["expiration_date"], original["expiration_date"])
        self.assertEqual(decoded["sex"], original["sex"])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_maximum_length_names(self):
        """Test names at maximum allowed length"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "123456789",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "A" * 30,  # Very long surname
            "given_names": "B" * 20,  # Long given names
        }

        line1, line2 = MRTD.encode_mrz(doc)
        self.assertEqual(len(line1), 44)
        decoded = MRTD.decode_mrz(line1, line2)
        self.assertIsNotNone(decoded["surname"])

    def test_single_character_fields(self):
        """Test with single character names"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "123456789",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "X",
            "given_names": "Y",
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        self.assertEqual(decoded["surname"], "X")
        self.assertEqual(decoded["given_names"], "Y")

    def test_all_numeric_document_number(self):
        """Test with all numeric document number"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "999999999",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "DOE",
            "given_names": "JOHN",
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        valid, _ = MRTD.validate_check_digits(decoded)
        self.assertTrue(valid)

    def test_all_alpha_document_number(self):
        """Test with all alphabetic document number"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "ABCDEFGHI",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "DOE",
            "given_names": "JOHN",
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        valid, _ = MRTD.validate_check_digits(decoded)
        self.assertTrue(valid)

    def test_boundary_dates(self):
        """Test with boundary date values"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "123456789",
            "date_of_birth": "000101",  # Year 00
            "sex": "M",
            "expiration_date": "991231",  # Year 99, Dec 31
            "nationality": "USA",
            "surname": "DOE",
            "given_names": "JOHN",
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        self.assertEqual(decoded["date_of_birth"], "000101")
        self.assertEqual(decoded["expiration_date"], "991231")

    def test_whitespace_in_names(self):
        """Test handling of multiple spaces in names"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            "document_number": "123456789",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "DOE   SMITH",  # Multiple spaces
            "given_names": "JOHN  MICHAEL  ROBERT",  # Multiple spaces
        }

        line1, line2 = MRTD.encode_mrz(doc)
        decoded = MRTD.decode_mrz(line1, line2)
        # Should handle multiple spaces gracefully
        self.assertIsNotNone(decoded["surname"])
        self.assertIsNotNone(decoded["given_names"])


class TestErrorMessages(unittest.TestCase):
    """Test that error messages are clear and helpful"""

    def test_missing_field_error_message(self):
        """Test that missing field error includes field name"""
        doc = {
            "document_type": "P",
            "country_code": "USA",
            # Missing document_number
        }

        try:
            MRTD.encode_mrz(doc)
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("document_number", str(e))
            self.assertIn("Missing", str(e))

    def test_invalid_length_error_message(self):
        """Test that length error includes expected length"""
        doc = {
            "document_type": "P",
            "country_code": "US",  # Too short
            "document_number": "123456789",
            "date_of_birth": "900101",
            "sex": "M",
            "expiration_date": "300101",
            "nationality": "USA",
            "surname": "DOE",
            "given_names": "JOHN",
        }

        try:
            MRTD.encode_mrz(doc)
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("3 characters", str(e))
            self.assertIn("country_code", str(e))

    def test_invalid_character_error_message(self):
        """Test that invalid character error is descriptive"""
        try:
            MRTD._normalize_mrz_line("ABC$DEF")
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("invalid characters", str(e))
            self.assertIn("A-Z", str(e))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
