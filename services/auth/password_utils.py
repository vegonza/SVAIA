from werkzeug.security import generate_password_hash, check_password_hash

def hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def check(password, hash):
    return check_password_hash(hash, password)