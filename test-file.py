def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: A list or iterable of numeric values.

    Returns:
        float: The average of all numbers in the list.
        int: Returns 0 if the list is empty.

    Example:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
        >>> calculate_average([])
        0
    """
    if not numbers:
        return 0
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def get_user_name(user):
    """
    Extract and format a user's name from a user dictionary.

    Args:
        user: A dictionary containing user information with a 'name' key.

    Returns:
        str: The user's name in uppercase. Returns an empty string if:
             - user is None or empty
             - 'name' key is not present
             - name value is None

    Example:
        >>> get_user_name({"name": "john doe"})
        'JOHN DOE'
        >>> get_user_name({})
        ''
        >>> get_user_name({"name": None})
        ''
    """
    if not user or "name" not in user:
        return ""
    name = user["name"]
    if name is None:
        return ""
    return str(name).upper()