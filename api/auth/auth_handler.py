import time
from typing import Dict
import jwt

JWT_SECRET = 'c3544c754bec26d6665dcb1c47668388a995f347036a1d66'
JWT_ALGORITHM = 'HS256'

def token_response(token: str, expires: int) -> Dict[str, str]:
    return { "access_token": token , "expires": expires }

def signJWT(user: str) -> Dict[str, str]:
    payload = {
        "user": user,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token, payload["expires"])

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] > time.time() else None
    except:
        return {}