import bcrypt
import shortuuid

from app.config import SECRET_KEY, TOKEN_EXPIRES, UUID_LEN, UUID_ALPHABET
from cryptography.fernet import Fernet, InvalidToken

def get_secret_key():
    return Fernet(SECRET_KEY)

def uuid():
    return shortuuid.ShortUUID(alphabet=UUID_ALPHABET).random(UUID_LEN)

def encrypt_token(random_id):
    secret_key = get_secret_key()
    return secret_key.encrypt(random_id.encode('utf-8'))

def decrypt_token(token):
    try:
        secret_key = get_secret_key()
        return secret_key.decrypt(token.encode('utf-8'))
    except InvalidToken:
        return None

