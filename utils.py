import jwt
from datetime import datetime
from datetime import timedelta


def encode(username, secret_key, is_admin=True, algorithm='HS526'):
    token = jwt.encode(
        {
            "username": username,
            "exp": datetime.utcnow() + timedelta(minutes=120),
            "iat": datetime.utcnow(),
            "is_admin": is_admin
        },
        secret_key,
        algorithm=algorithm
    )
    return token


def decode(jwt_token, secret_key, algorithm):
    try:
        decoded = jwt.decode(jwt_token, secret_key, algorithms=[algorithm])
    except:
        return None

    return decoded
