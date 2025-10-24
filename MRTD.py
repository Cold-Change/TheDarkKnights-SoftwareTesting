import re
from typing import Tuple, Dict, List, Any


# -------------------------
# Exceptions
# -------------------------
class ScannerError(Exception):
    """Raised when hardware MRZ scanning fails (or is not implemented)."""
    pass


# -------------------------
# Helper utilities
# -------------------------
_WEIGHTS = [7, 3, 1]  # repeating weights for ICAO check digit calculation

# Allowed characters in MRZ per spec: A-Z, 0-9 and '<'
_ALLOWED_MRZ_REGEX = re.compile(r'^[A-Z0-9<]+$')


def _char_value(ch: str) -> int:
    """Return numeric value used for check digits:
       0-9 -> 0-9, A-Z -> 10-35, '<' -> 0
    """
    if ch == '<':
        return 0
    if '0' <= ch <= '9':
        return ord(ch) - ord('0')
    # letter
    return ord(ch) - ord('A') + 10


def compute_check_digit(field: str) -> str:
    """
    Compute the ICAO 9303 check digit for a given field (string).
    Returns single character string '0'..'9'.
    """
    total = 0
    for i, ch in enumerate(field):
        val = _char_value(ch)
        weight = _WEIGHTS[i % 3]
        total += val * weight
    return str(total % 10)


def _ensure_line_length(line: str, name: str) -> None:
    if len(line) != 44:
        raise ValueError(f"{name} must be exactly 44 characters long (got {len(line)}).")


def _normalize_mrz_line(line: str) -> str:
    """Upper-case, convert spaces to '<' and validate allowed characters.
       Raises ValueError if invalid characters present.
    """
    if line is None:
        raise ValueError("MRZ line is None")
    # replace lowercase with uppercase
    s = line.upper()
    s = s.replace(' ', '<')  # accept spaces and convert to filler
    if not _ALLOWED_MRZ_REGEX.match(s):
        raise ValueError("MRZ line contains invalid characters (allowed A-Z, 0-9, '<').")
    return s


def _strip_fillers(value: str) -> str:
    """Remove trailing/leading fillers and convert single fillers to separators (space)."""
    # remove trailing and leading fillers
    stripped = value.strip('<')
    # replace consecutive fillers with single space, single filler with space for name parts
    if '<' in stripped:
        # collapse repeated '<' into single separator between name parts
        # but we treat multiple as a separator; convert any runs of '<' to a single space
        stripped = re.sub(r'<+', ' ', stripped)
    return stripped


# -------------------------
# Public Interface
# -------------------------
def scan_mrz() -> Tuple[str, str]:
    """
    Placeholder interface to hardware scanner. According to requirements:
    - Should return (line1, line2) strings when implemented.
    - Should raise ScannerError if scanning fails.
    Since hardware integration is out of scope, this function raises ScannerError
    to indicate it is not implemented.
    """
    raise ScannerError("scan_mrz() is not implemented: hardware scanner integration not available.")


def decode_mrz(line1: str, line2: str) -> Dict[str, Any]:
    """
    Decode two MRZ strings (TD-3 passport format) into their respective fields.
    Validates allowed characters and length (44 chars each). Converts lowercase to uppercase.
    Removes filler characters when presenting field values.

    Returns a dictionary containing keys per spec, including check digits as separate keys.
    """
    if line1 is None or line2 is None:
        raise ValueError("Both MRZ lines must be provided.")

    # Normalize and validate characters
    l1 = _normalize_mrz_line(line1)
    l2 = _normalize_mrz_line(line2)

    # Validate length
    _ensure_line_length(l1, "line1")
    _ensure_line_length(l2, "line2")

    # Positions per TD-3 (1-indexed in spec). Convert to 0-indexed slices.
    # line1: pos 1-2 doc type, 3-5 issuing country, 6-44 names (positions inclusive)
    doc_type = l1[0:2]  # 2 chars
    issuing_country = l1[2:5]  # 3 chars
    names_raw = l1[5:44]  # 39 chars

    # line2 fields
    document_number = l2[0:9]  # 9 chars
    document_number_check = l2[9]  # 1 char
    nationality = l2[10:13]  # 3 chars
    dob = l2[13:19]  # 6 chars (YYMMDD)
    dob_check = l2[19]  # 1 char
    sex = l2[20]  # 1 char
    expiry = l2[21:27]  # 6 chars (YYMMDD)
    expiry_check = l2[27]  # 1 char
    personal_number = l2[28:42]  # 14 chars
    personal_number_check = l2[42]  # 1 char
    composite_check = l2[43]  # 1 char

    # Process names: format SURNAME<<GIVEN<NAMES....
    # names_raw may contain filler '<' characters; we treat '<<' as separator between surname and given names.
    # Replace sequences of '<' with separators accordingly, then strip.
    surname_part = ""
    given_part = ""
    if '<<' in names_raw:
        surname_part_raw, given_part_raw = names_raw.split('<<', 1)
        surname_part = _strip_fillers(surname_part_raw)
        given_part = _strip_fillers(given_part_raw)
    else:
        # if no '<<' found, take everything as surname and empty given name
        surname_part = _strip_fillers(names_raw)
        given_part = ""

    # produce cleaned fields (no filler characters)
    result = {
        "document_type": doc_type.replace('<', '').strip(),
        "issuing_country": issuing_country.replace('<', '').strip(),
        "surname": surname_part,
        "given_names": given_part,
        "document_number": document_number,
        "document_number_clean": _strip_fillers(document_number),
        "document_number_check": document_number_check,
        "nationality": nationality.replace('<', '').strip(),
        "date_of_birth": dob,
        "date_of_birth_check": dob_check,
        "sex": sex if sex != '<' else '',
        "expiration_date": expiry,
        "expiration_date_check": expiry_check,
        "personal_number": personal_number,
        "personal_number_clean": _strip_fillers(personal_number),
        "personal_number_check": personal_number_check,
        "composite_check": composite_check,
        # Keep raw lines for traceability
        "_raw_line1": l1,
        "_raw_line2": l2
    }

    return result


def get_travel_doc_from_db(doc_id: str) -> Dict[str, Any]:
    """
    Placeholder for database retrieval. Returns mock travel document data for testing.
    Fields returned:
    - document_type (1 or 2 chars, e.g., 'P<')
    - country_code (3 chars)
    - document_number (<=9 chars)
    - date_of_birth (YYMMDD)
    - sex ('M'/'F'/'<')
    - expiration_date (YYMMDD)
    - nationality (3 chars)
    - surname (string)
    - given_names (string, possibly multiple names separated by spaces)
    - personal_number (optional, up to 14 chars)
    """
    # NOTE: In production this would query the DB. For now, return a mock.
    mock = {
        "document_type": "P",  # single char OK; will be padded to 2
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
    return mock


def _pad_field(value: str, length: int) -> str:
    """Pad a field to exact length using '<' filler (right padding)."""
    v = value or ''
    if len(v) > length:
        return v[:length]
    return v + ('<' * (length - len(v)))


def _validate_field_chars(field: str, allow_letters_spaces: bool = False) -> None:
    """
    Validate characters for MRZ:
      - allowed A-Z, 0-9, and '<'
    For names, allow letters and spaces (we will convert spaces to '<' during encoding).
    """
    if allow_letters_spaces:
        # allow letters, spaces, hyphen, apostrophe in source names — will map to MRZ allowed chars
        if not re.match(r'^[A-Za-z \-\'\.]+$', field):
            raise ValueError("Name contains invalid characters (allowed letters, spaces, hyphen, apostrophe, dot).")
    else:
        # MRZ field must only contain A-Z, 0-9 and '<' (we will uppercase and pad)
        if not _ALLOWED_MRZ_REGEX.match(field):
            raise ValueError("Field contains invalid characters (allowed A-Z, 0-9, '<').")


def _format_name_field(surname: str, given_names: str, max_length: int = 39) -> str:
    """
    Format the name field per requirement:
    SURNAME<<GIVEN_NAMES
    - Multiple given name parts separated by single '<'
    - Surname and given names separated by '<<'
    - Spaces in names converted to '<'
    - Truncate to max_length if needed
    - Right-pad with '<' to fill remaining space
    """
    # Replace invalid chars and convert to uppercase
    if surname is None:
        surname = ''
    if given_names is None:
        given_names = ''
    # Clean whitespace
    surname_clean = ' '.join(surname.strip().split())
    given_clean = ' '.join(given_names.strip().split())

    # Validate characters in names (allow letters, hyphen, apostrophe, dot)
    _validate_field_chars(surname_clean, allow_letters_spaces=True)
    _validate_field_chars(given_clean, allow_letters_spaces=True)

    # Convert to uppercase
    surname_up = surname_clean.upper()
    given_up = given_clean.upper()

    # Replace spaces between name parts with single filler '<'
    # For given names, separate multi-part given names with single '<'
    given_up_mrz = re.sub(r'\s+', '<', given_up) if given_up else ''
    surname_up_mrz = re.sub(r'\s+', '<', surname_up) if surname_up else ''

    # Combine surname and given names with '<<'
    combined = f"{surname_up_mrz}<<{given_up_mrz}" if given_up_mrz else f"{surname_up_mrz}<<"

    # Replace any characters that are not allowed in MRZ for names (only letters, digits, and '<' allowed).
    # Common punctuation like hyphens/apostrophes are not allowed in MRZ — they should be removed or replaced.
    combined = re.sub(r"[^A-Z0-9<]", '', combined)

    # Truncate and pad to exact max_length
    if len(combined) > max_length:
        combined = combined[:max_length]
    combined = _pad_field(combined, max_length)
    return combined


def encode_mrz(travel_doc_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Encode travel document fields into two MRZ lines (TD-3 standard), each exactly 44 characters.
    travel_doc_data dictionary must contain keys:
      document_type, country_code, document_number, date_of_birth (YYMMDD),
      sex, expiration_date (YYMMDD), nationality, surname, given_names
    personal_number is optional (if omitted, use '<' padding).
    This function validates inputs, pads fields, computes check digits and returns (line1, line2).
    """
    # Required fields
    required = ["document_type", "country_code", "document_number", "date_of_birth",
                "sex", "expiration_date", "nationality", "surname", "given_names"]
    for k in required:
        if k not in travel_doc_data or travel_doc_data[k] is None:
            raise ValueError(f"Missing required field for encoding: {k}")

    # Normalize and validate basic fields
    doc_type = travel_doc_data["document_type"].upper()
    if len(doc_type) == 0:
        raise ValueError("document_type must be non-empty")
    # pad to 2 chars (doc-type + optional filler)
    doc_type_field = _pad_field(doc_type.replace(' ', '<'), 2)

    country_code = travel_doc_data["country_code"].upper()
    if len(country_code) != 3:
        raise ValueError("country_code must be exactly 3 characters")
    country_code_field = country_code

    # Document number: allowed chars A-Z0-9, max 9
    doc_number_raw = str(travel_doc_data["document_number"]).upper()
    # Replace spaces with filler (not typical but safe)
    doc_number_raw = doc_number_raw.replace(' ', '<')
    # Validate allowed characters (allow letters and digits only)
    if not re.match(r'^[A-Z0-9<]*$', doc_number_raw):
        raise ValueError("document_number contains invalid characters (only A-Z, 0-9 allowed).")
    document_number_field = _pad_field(doc_number_raw, 9)

    # Date validation (YYMMDD) numeric
    dob = str(travel_doc_data["date_of_birth"])
    if not re.match(r'^\d{6}$', dob):
        raise ValueError("date_of_birth must be in YYMMDD numeric format")
    dob_field = dob

    sex = travel_doc_data["sex"].upper() if travel_doc_data["sex"] else '<'
    if sex not in ['M', 'F', '<', 'X']:
        # Allow X or other unknown codes; map invalid to '<'
        raise ValueError("sex must be 'M', 'F', 'X' or '<'")

    expiry = str(travel_doc_data["expiration_date"])
    if not re.match(r'^\d{6}$', expiry):
        raise ValueError("expiration_date must be in YYMMDD numeric format")
    expiry_field = expiry

    nationality = travel_doc_data["nationality"].upper()
    if len(nationality) != 3:
        raise ValueError("nationality must be exactly 3 characters")
    nationality_field = nationality

    # Personal number (optional) up to 14 chars
    personal_number_raw = travel_doc_data.get("personal_number", "") or ""
    personal_number_raw = str(personal_number_raw).upper().replace(' ', '<')
    if personal_number_raw and not re.match(r'^[A-Z0-9<]*$', personal_number_raw):
        raise ValueError("personal_number contains invalid characters (only A-Z, 0-9 allowed).")
    personal_number_field = _pad_field(personal_number_raw, 14)

    # Name field formatting
    name_field = _format_name_field(travel_doc_data["surname"], travel_doc_data["given_names"], max_length=39)

    # Now compute check digits
    doc_number_check = compute_check_digit(document_number_field)
    dob_check = compute_check_digit(dob_field)
    expiry_check = compute_check_digit(expiry_field)
    personal_number_check = compute_check_digit(personal_number_field)

    # Composite check: concatenate fields in this order:
    # document_number (9) + document_number_check (1) + dob (6) + dob_check (1) +
    # expiry (6) + expiry_check (1) + personal_number (14) + personal_number_check (1)
    composite_input = (
        document_number_field +
        doc_number_check +
        dob_field +
        dob_check +
        expiry_field +
        expiry_check +
        personal_number_field +
        personal_number_check
    )
    composite_check = compute_check_digit(composite_input)

    # Build line1 (44 chars): doc_type_field (2) + country_code_field (3) + name_field (39)
    line1 = doc_type_field + country_code_field + name_field
    if len(line1) != 44:
        # Defensive: pad or error
        line1 = _pad_field(line1, 44)

    # Build line2 (44 chars):
    # document_number (9) + doc_number_check (1) + nationality (3) + dob (6) + dob_check (1) +
    # sex (1) + expiry (6) + expiry_check (1) + personal_number (14) + personal_number_check (1) + composite_check (1)
    line2 = (
        document_number_field +
        doc_number_check +
        nationality_field +
        dob_field +
        dob_check +
        (sex if sex else '<') +
        expiry_field +
        expiry_check +
        personal_number_field +
        personal_number_check +
        composite_check
    )
    if len(line2) != 44:
        # Defensive padding
        line2 = _pad_field(line2, 44)

    # Final validation of allowed characters
    if not _ALLOWED_MRZ_REGEX.match(line1) or not _ALLOWED_MRZ_REGEX.match(line2):
        raise ValueError("Generated MRZ lines contain invalid characters.")

    return line1, line2


def validate_check_digits(decoded: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Validate all check digits found in a decoded MRZ dictionary.
    Returns:
      - (True, "All check digits valid") if everything matches
      - (False, errors_list) if any mismatches; errors_list is a list of dictionaries
        with keys: field_name, expected, actual, position, message
    The decoded dict is expected to be the output of decode_mrz().
    """
    errors: List[Dict[str, Any]] = []

    # Helper to compare and append error if mismatch
    def _cmp(field_label: str, value_field: str, actual_check: str, position: int):
        """value_field must be a MRZ padded string with fillers where required."""
        expected = compute_check_digit(value_field)
        if expected != actual_check:
            errors.append({
                "field_name": field_label,
                "expected": expected,
                "actual": actual_check,
                "position": position,
                "message": f"Check digit mismatch for {field_label}: expected {expected}, got {actual_check}."
            })

    # Document number: ensure it's exactly 9 chars (padded) for calculation
    doc_num = decoded.get("document_number")
    if doc_num is None:
        raise ValueError("Decoded MRZ missing 'document_number' field.")
    # document_number in decode_mrz is retained as raw 9-char slice
    _cmp("document_number", doc_num, decoded.get("document_number_check", ""), position=10)

    # DOB (positions 14-19 -> index positions note we use spec 1-indexing in messages)
    dob = decoded.get("date_of_birth")
    _cmp("date_of_birth", dob, decoded.get("date_of_birth_check", ""), position=20)

    # Expiration date
    expiry = decoded.get("expiration_date")
    _cmp("expiration_date", expiry, decoded.get("expiration_date_check", ""), position=28)

    # Personal number (14 chars)
    personal = decoded.get("personal_number")
    _cmp("personal_number", personal, decoded.get("personal_number_check", ""), position=43)

    # Composite check digit: must be computed over concatenation:
    # document_number (9) + doc_number_check (1) + dob (6) + dob_check(1) +
    # expiry (6) + expiry_check (1) + personal_number (14) + personal_number_check (1)
    composite_input = (
        decoded.get("document_number", "") +
        decoded.get("document_number_check", "") +
        decoded.get("date_of_birth", "") +
        decoded.get("date_of_birth_check", "") +
        decoded.get("expiration_date", "") +
        decoded.get("expiration_date_check", "") +
        decoded.get("personal_number", "") +
        decoded.get("personal_number_check", "")
    )
    expected_composite = compute_check_digit(composite_input)
    actual_composite = decoded.get("composite_check", "")
    if expected_composite != actual_composite:
        errors.append({
            "field_name": "composite_check",
            "expected": expected_composite,
            "actual": actual_composite,
            "position": 44,
            "message": f"Composite check digit mismatch: expected {expected_composite}, got {actual_composite}."
        })

    if not errors:
        return True, "All check digits valid"
    else:
        # Return False and the structured errors list
        return False, errors


# -------------------------
# If run directly: small demo (won't call hardware)
# -------------------------
if __name__ == "__main__":
    # Simple demonstration of encode -> decode -> validate cycle using mock DB data.
    print("MRTD module demo: encode -> decode -> validate using mock DB data")
    doc = get_travel_doc_from_db("mock-id")
    line1, line2 = encode_mrz(doc)
    print("Encoded MRZ:")
    print(line1)
    print(line2)

    decoded = decode_mrz(line1, line2)
    print("\nDecoded fields (clean):")
    for k, v in decoded.items():
        if not k.startswith('_'):
            print(f"{k}: {v}")

    valid, info = validate_check_digits(decoded)
    print("\nValidation result:", valid)
    print("Info:", info)
