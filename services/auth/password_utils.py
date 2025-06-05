from werkzeug.security import generate_password_hash, check_password_hash
from typeguard import typechecked


@typechecked
def hash(password: str) -> str:
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


@typechecked
def check(password: str, hash: str) -> bool:
    return check_password_hash(hash, password)
