# crypto_utils.py
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoUtils:
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Создать ключ из мастер-пароля и соли"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=10000,
        )
        return kdf.derive(password.encode())

    @staticmethod
    def encrypt(key: bytes, plaintext: str) -> bytes:
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        return nonce + ciphertext

    @staticmethod
    def decrypt(key: bytes, data: bytes) -> str:
        aesgcm = AESGCM(key)
        nonce, ct = data[:12], data[12:]
        return aesgcm.decrypt(nonce, ct, None).decode()