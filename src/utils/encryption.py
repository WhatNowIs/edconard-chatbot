import hashlib
import json
import os

def encrypt(value: str) -> tuple[str, str]:
    """Hash the value and generate a salt."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', value.encode(), salt, 100000)
    return dk.hex(), salt.hex()

def verify(value: str, hashed_value: str, salt: str) -> bool:
    """Verify if the provided value matches the stored value."""
    dk = hashlib.pbkdf2_hmac('sha256', value.encode(), bytes.fromhex(salt), 100000)
    return dk.hex() == hashed_value

def generate_hash(*args):
    """Generates a SHA-256 hash of the given arguments.

    Args:
        *args: Variable length argument list. Each argument can be of any type that
               can be converted to a string or is a JSON serializable object.

    Returns:
        A hexadecimal string representing the SHA-256 hash of the arguments.
    """
    hasher = hashlib.sha256()

    for arg in args:
        if isinstance(arg, (dict, list)):
            # Ensure consistent ordering for JSON serializable objects
            arg_str = json.dumps(arg, sort_keys=True)
        else:
            # Convert other types to string
            arg_str = str(arg)
        hasher.update(arg_str.encode("utf-8"))
    return hasher.hexdigest()
