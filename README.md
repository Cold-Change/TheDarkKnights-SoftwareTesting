# TheDarkKnights-SoftwareTesting

Software testing project for MRTD (Machine Readable Travel Document) system implementing ICAO 9303 TD-3 passport MRZ standard.

## Project Structure

### MRTD.py

Implements MRZ scanning/decoding/encoding/check-digit validation helpers for ICAO 9303 TD-3 (passport) MRZs.

#### Main Functions:
- `scan_mrz()` - Placeholder for hardware scanner integration (raises ScannerError)
- `decode_mrz(line1, line2)` - Decodes two MRZ strings into decoded fields dictionary (validates allowed chars, sizes)
- `encode_mrz(travel_doc_data)` - Encodes travel document data into (line1, line2) strings of length 44 each
- `get_travel_doc_from_db(doc_id)` - Placeholder that returns mock travel document data for testing
- `validate_check_digits(decoded_mrz_dict)` - Validates all check digits, returns (bool, message_or_errors)

#### Helper Functions:
- `compute_check_digit(field)` - Computes ICAO 9303 check digit for a given field
- `_char_value(ch)` - Returns numeric value for check digit calculation (0-9, A-Z, '<')
- `_normalize_mrz_line(line)` - Uppercases, converts spaces to '<', validates characters
- `_strip_fillers(value)` - Removes trailing/leading fillers and converts to separators
- `_pad_field(value, length)` - Pads field to exact length with '<' filler
- `_format_name_field(surname, given_names, max_length)` - Formats names per MRZ standard
- `_validate_field_chars(field, allow_letters_spaces)` - Validates MRZ allowed characters

### MRTDtest.py

Comprehensive test suite for MRTD.py with **80 unit and integration tests** covering all functions with various scenarios including edge cases, error handling, and validation.

## Test Coverage

### Test Classes and Coverage:

1. **TestCharValue** (3 tests)
   - Character value mapping for filler, digits, and letters

2. **TestComputeCheckDigit** (5 tests)
   - Basic check digit calculation
   - Check digits with letters, empty strings, all fillers
   - Known value verification

3. **TestNormalizeMrzLine** (6 tests)
   - Uppercase conversion
   - Space-to-filler conversion
   - Invalid character detection
   - None input handling

4. **TestStripFillers** (6 tests)
   - Leading/trailing filler removal
   - Multiple filler to space conversion
   - Complex patterns

5. **TestPadField** (5 tests)
   - Padding shorter strings
   - Exact length handling
   - Truncation of longer strings
   - Empty and None values

6. **TestScanMrz** (1 test)
   - ScannerError exception verification

7. **TestDecodeMrz** (13 tests)
   - Valid MRZ decoding
   - All field extraction
   - None/null input validation
   - Wrong length detection
   - Invalid characters
   - Lowercase conversion
   - Name parsing variations
   - Sex field handling
   - Document/personal number cleaning

8. **TestEncodeMrz** (18 tests)
   - Valid document encoding
   - Missing/null required fields
   - Invalid country codes and nationalities
   - Date format validation (YYMMDD)
   - Sex value validation (M/F/X/<)
   - Document type validation
   - Personal number handling
   - Long names/numbers truncation
   - Special characters in names
   - Multiple given names
   - Case conversion

9. **TestValidateCheckDigits** (4 tests)
   - Valid check digit verification
   - Invalid check digit detection
   - Multiple error detection
   - Error structure validation
   - Missing field handling

10. **TestGetTravelDocFromDb** (3 tests)
    - Return type verification
    - Required fields presence
    - Field format validation

11. **TestIntegration** (5 tests)
    - Full encode→decode→validate cycle
    - Minimal required fields
    - Complex names
    - Personal number preservation
    - Data roundtrip integrity

12. **TestEdgeCases** (6 tests)
    - Maximum length names
    - Single character fields
    - All-numeric/all-alphabetic document numbers
    - Boundary date values
    - Multiple spaces in names

13. **TestErrorMessages** (3 tests)
    - Clear error message validation
    - Descriptive length errors
    - Invalid character errors

## Requirements

- Python 3.x
- Coverage package (for code coverage analysis)

## Setup Instructions

### 1. Activate Conda Environment
```powershell
conda activate your-env-name
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

Or install coverage directly:
```powershell
pip install coverage
```

## Running the Tests

### Basic Test Execution

Run the complete test suite:
```bash
python -m unittest MRTDtest -v
```

Run specific test class:
```bash
python -m unittest MRTDtest.TestDecodeMrz -v
```

Run specific test:
```bash
python -m unittest MRTDtest.TestDecodeMrz.test_decode_valid_mrz -v
```

### Running with Coverage

**PowerShell commands (for Windows/VS Code):**

Run tests with coverage:
```powershell
python -m coverage run -m unittest MRTDtest
```

View coverage report:
```powershell
python -m coverage report
```

View detailed coverage with line numbers:
```powershell
python -m coverage report -m
```

Generate HTML coverage report:
```powershell
python -m coverage html
```

Open HTML report in browser:
```powershell
start htmlcov\index.html
```

**Quick one-liner (PowerShell):**
```powershell
python -m coverage run -m unittest MRTDtest; python -m coverage report -m
```

**Or use the provided script:**
```powershell
.\run_coverage.ps1
```

## Test Results

**Total Tests: 80**
**Status: All Passing ✓**

**Coverage Results:**
- **MRTD.py:** 87% coverage (194 statements)
- **MRTDtest.py:** 99% coverage (445 statements)
- **Overall:** 95% coverage

The test suite provides comprehensive coverage of:
- ✅ All public functions
- ✅ All helper functions
- ✅ Error handling and validation
- ✅ Edge cases and boundary conditions
- ✅ Integration testing
- ✅ Clear, descriptive error messages
