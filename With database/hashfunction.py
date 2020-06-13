from hashlib import sha256


def get_hash(data, simple_hash=False):
    """
    input: data - string
    output: string, hash of data by sha256 algorithm
    """
    if simple_hash:
        return data
    return sha256(data.encode()).hexdigest()
