import re
from datetime import date
from django.core.exceptions import ValidationError

def normalize_isbn(value):
    text=re.sub(r"[\s-]", "", value or "").upper()
    if not text:
        return None
    if len(text)==10 and re.fullmatch(r"[0-9]{9}[0-9X]",text):
        digits=[int(c) if c!="X" else 10 for c in text]
        if sum((10-i)*n for i,n in enumerate(digits))%11:
            raise ValidationError("Invalid ISBN checksum.")
        text="978"+text[:9]
        text+=str((-sum(int(c)*(1 if i%2==0 else 3) for i,c in enumerate(text)))%10)
    if not re.fullmatch(r"97[89][0-9]{10}",text) or sum(int(c)*(1 if i%2==0 else 3) for i,c in enumerate(text))%10:
        raise ValidationError("Provide a valid ISBN-10 or ISBN-13.")
    return text

def validate_isbn(value):
    normalize_isbn(value)

def parse_publication(value):
    value=(value or "").strip()
    if not value:
        return "",None
    if not re.fullmatch(r"[0-9]{4}(?:-[0-9]{2})?(?:-[0-9]{2})?",value):
        raise ValidationError("Publication date must be YYYY, YYYY-MM or YYYY-MM-DD.")
    parts=[int(x) for x in value.split("-")]
    try:
        parsed=date(*(parts+[1]*(3-len(parts))))
    except ValueError as exc:
        raise ValidationError("Invalid publication date.") from exc
    return value,parsed if len(parts)==3 else None