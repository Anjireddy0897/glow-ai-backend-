import re

def validate_password(value):
    errors = []
    if len(value) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', value):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', value):
        errors.append("Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        errors.append("Password must contain at least one special character.")
    return errors

# Test cases
test_data = [
    ("abc1!", ["Password must be at least 8 characters long.", "Password must contain at least one uppercase letter."]),
    ("noupper1!", ["Password must contain at least one uppercase letter."]),
    ("ALLUPPER1!", []),
    ("NoNumber!", ["Password must contain at least one number."]),
    ("NoSpecial1", ["Password must contain at least one special character."]),
    ("Password123", ["Password must contain at least one special character."]),
    ("Pass123!", []),
    ("Password1!", []),
]

for pwd, expected in test_data:
    actual = validate_password(pwd)
    if set(actual) == set(expected):
        print(f"PASS: {pwd}")
    else:
        print(f"FAIL: {pwd} | Expected: {expected} | Actual: {actual}")
