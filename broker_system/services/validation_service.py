# services/validation_service.py


REQUIRED_HQ_FIELDS = [
    "Do you smoke",
    "Height",
    "Weight",
    "Medical history",
    "Signature",
    "Date"
]


def validate_hq_form(text):
    missing_fields = []

    for field in REQUIRED_HQ_FIELDS:
        if field.lower() not in text.lower():
            missing_fields.append(field)

    if missing_fields:
        return {
            "status": "incomplete",
            "missing": missing_fields
        }

    return {
        "status": "complete",
        "missing": []
    }