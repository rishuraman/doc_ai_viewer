# extractor/fields.py
import re

def extract_fields(doc_type: str, text: str) -> dict:
    t = text  # keep original case for nicer display
    u = text.upper()

    result: dict[str, str | None] = {}

    if doc_type == "Driving License":
        # ... your DL extraction
        pass

    elif doc_type == "Flood Certificate":
        # ...
        pass

    elif doc_type == "W2":
        # ...
        pass

    elif doc_type == "Paystub":
        # ...
        pass

    elif doc_type == "Passport":
        result["name"] = extract_passport_name(t)
        result["passport_number"] = extract_passport_number(t)
        result["country"] = extract_passport_country(t)
        result["dob"] = extract_passport_dob(t)
        result["expire_date"] = extract_passport_expiry(t)

    return result
