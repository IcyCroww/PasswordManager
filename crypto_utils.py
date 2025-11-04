# crypto_utils.py - Полностью исправленная криптография
import os
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoUtils:
    """Криптографические утилиты с максимальной безопасностью"""

    # Современные параметры безопасности (2024)
    ITERATIONS = 600000  # OWASP рекомендация
    KEY_LENGTH = 32  # AES-256
    SALT_LENGTH = 32  # 256 бит
    NONCE_LENGTH = 12  # AES-GCM стандарт

    @staticmethod
    def generate_salt() -> bytes:
        """Генерация криптографически стойкой соли"""
        return secrets.token_bytes(CryptoUtils.SALT_LENGTH)

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Генерация криптографически стойкого токена"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Создание ключа из пароля с помощью PBKDF2-HMAC-SHA256

        Args:
            password: Мастер-пароль пользователя
            salt: Соль (должна быть уникальной для каждой БД)

        Returns:
            32-байтовый ключ для AES-256
        """
        if not password:
            raise ValueError("Пароль не может быть пустым")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=CryptoUtils.KEY_LENGTH,
            salt=salt,
            iterations=CryptoUtils.ITERATIONS,
        )
        return kdf.derive(password.encode('utf-8'))

    @staticmethod
    def encrypt(key: bytes, plaintext: str) -> bytes:
        """
        Шифрование текста с помощью AES-256-GCM

        Args:
            key: 32-байтовый ключ шифрования
            plaintext: Текст для шифрования

        Returns:
            nonce (12 байт) + ciphertext
        """
        if len(key) != CryptoUtils.KEY_LENGTH:
            raise ValueError(f"Ключ должен быть {CryptoUtils.KEY_LENGTH} байт")

        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(CryptoUtils.NONCE_LENGTH)

        try:
            ciphertext = aesgcm.encrypt(
                nonce,
                plaintext.encode('utf-8'),
                None  # AAD (дополнительные данные) не используем
            )
            return nonce + ciphertext
        except Exception as e:
            raise RuntimeError(f"Ошибка шифрования: {e}")

    @staticmethod
    def decrypt(key: bytes, data: bytes) -> str:
        """
        Расшифровка данных AES-256-GCM

        Args:
            key: 32-байтовый ключ шифрования
            data: nonce + ciphertext

        Returns:
            Расшифрованный текст
        """
        if len(key) != CryptoUtils.KEY_LENGTH:
            raise ValueError(f"Ключ должен быть {CryptoUtils.KEY_LENGTH} байт")

        if len(data) < CryptoUtils.NONCE_LENGTH:
            raise ValueError("Данные повреждены: слишком короткие")

        nonce = data[:CryptoUtils.NONCE_LENGTH]
        ciphertext = data[CryptoUtils.NONCE_LENGTH:]

        aesgcm = AESGCM(key)

        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Ошибка расшифровки: неверный пароль или повреждённые данные")