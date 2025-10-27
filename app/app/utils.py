import re

def normalize_phone_number(phone):
    """
    Cleans and standardizes a phone number.
    - Removes all non-digit characters.
    - If it's 10 digits, assumes it's a local number and adds '+91'.
    - If it's 12 digits and starts with '91', adds '+'.
    - If it starts with '+', it's already good.
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        # Assumes 10 digits is an Indian number
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith('91'):
        # Assumes 91... is an Indian number, adds '+'
        return f"+{digits}"
    elif phone.startswith('+'):
        # Already in international format
        return phone
    
    # Fallback for other formats (or you could raise an error)
    return phone