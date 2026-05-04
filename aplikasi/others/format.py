import hashlib


def generate_checksum(payload):
    return hashlib.sha256(payload.encode()).hexdigest()
