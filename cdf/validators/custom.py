import re

import warnings


def validate_formation(s):
    # Check format using regex
    pattern = r"^[1-5](-[1-5]){2,4}$"
    if not re.match(pattern, s):
        return False

    # Extract numbers and calculate sum
    numbers = [int(num) for num in s.split("-")]
    total = sum(numbers)

    return 7 <= total <= 10


class ValidationWarning(UserWarning):
    """Warning for validation issues."""

    pass
