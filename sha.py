import hashlib


def get_sha_256(string):
    encoded = string.encode()
    result = hashlib.sha256(encoded)

    return result.hexdigest()
