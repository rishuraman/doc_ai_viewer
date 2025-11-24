# extractor/classifier.py

def classify_document(text: str) -> str:
    t = text.upper()

    # ---- Passport FIRST: it's very distinctive ----
    if "PASSPORT" in t and "UNITED STATES OF AMERICA" in t:
        return "Passport"
    if "PASSPORT" in t and "NATIONALITY" in t:
        return "Passport"

    # ---- Driving License ----
    if (
        ("DRIVER" in t or "DRIVING" in t)
        and ("LICENSE" in t or "LICENCE" in t or "DL" in t)
    ) or "DL NO" in t or "DL NUMBER" in t:
        return "Driving License"

    # ---- Flood Certificate ----
    if "FLOOD" in t and "CERTIFICATE" in t:
        return "Flood Certificate"

    # ---- W2 ----
    if "FORM W-2" in t or "FORM W2" in t or "WAGE AND TAX STATEMENT" in t:
        return "W2"

    # ---- Paystub ----
    if (
        "PAY STUB" in t or "PAYSTUB" in t or "PAY SLIP" in t or "PAYSLIP" in t
        or "PAY STATEMENT" in t or "EARNINGS STATEMENT" in t
    ):
        return "Paystub"
    if "NET PAY" in t and ("HOURS" in t or "RATE" in t):
        return "Paystub"

    return "Others"
