# TheDarkKnights-SoftwareTesting

# MRTD.py

Implements MRZ scanning/decoding/encoding/check-digit validation helpers
for ICAO 9303 TD-3 (passport) MRZs.

Functions:
- scan_mrz() -> placeholder for hardware scanner integration (raises ScannerError)
- decode_mrz(line1, line2) -> dict of decoded fields (validates allowed chars, sizes)
- encode_mrz(travel_doc_data) -> (line1, line2) strings of length 44 each
- get_travel_doc_from_db(doc_id) -> placeholder that returns mock data for testing
- validate_check_digits(decoded_mrz_dict) -> (bool, message_or_errors)
