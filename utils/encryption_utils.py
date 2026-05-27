import string
import random
import json
import secrets

from typing import Any

from base64 import b64decode, b64encode

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from django.conf import settings

from utils.exception_utils import CustomException
from utils.helpers import logger


def encrypt_data_with_fernet(
    data: Any
) -> str | dict | None:
    fernet = Fernet(settings.FERNET_TOKEN_KEY.encode())
    encrypted_data = fernet.encrypt(data.encode()).decode()
    return encrypted_data


def decrypt_data_with_fernet(
    token: str | None
) -> str | dict | None:
    if not token:
        raise CustomException("Service unavailable at the moment. Try again later!", 502)
    fernet = Fernet(settings.FERNET_TOKEN_KEY.encode())
    decrypted = fernet.decrypt(token.encode()).decode()
    return decrypted


class AESOperations:

    ENCRYPTION_KEY_SOURCES = {
        "FLUTTERWAVE": settings.FLUTTERWAVE_ENCRYPTION_KEY,
    }


    def __init__(self, key: str | None = None, *args, **kwargs):
        source = kwargs.get("source", "FLUTTERWAVE")
        if (not key) and (not source or source not in self.ENCRYPTION_KEY_SOURCES):
            raise CustomException(
                "encryption key or valid key source must be provided for encryption operations!"
            )
        self.key: bytes = self._decode_key(key or self.ENCRYPTION_KEY_SOURCES[source])
        self.source = source
        logger.debug(f"encryption key used::::::: {self.key}\n key before decoding::::: {self.ENCRYPTION_KEY_SOURCES.get(source)}")


    def encrypt_data(
        self, data: dict | str | Any
    ) -> dict[str, str] | Any:
        """
        encrypts given data with AES algorithm
        """
        if self.source == "FLUTTERWAVE":
            nonce = self.generate_nonce(length=12)
            return self._encrypt_flutterwave_data_with_aes(data, nonce=nonce)
        return {}


    def decrypt_data(
        self, data: str | bytes
    ) -> dict | str | Any:
        """
        decrypts the aes encrypted data into its original form
        """


    def _decode_key(self, key: str | bytes) -> bytes:
        decoded_key = None
        if isinstance(key, str):
            decoded_key = self._decode_from_str(key)
            return decoded_key
        if isinstance(key, bytes):
            decoded_key = self._decode_from_bytes(key)
            return decoded_key
        try:
            decoded_key = b64encode(key)
        except Exception as e:
            raise CustomException("Invalid encryption key provided!", 400) from e
        return decoded_key


    def _decode_from_str(self, key: str) -> bytes:
        try:
            decoded_key = b64decode(key)
        except Exception as e:
            raise CustomException("Invalid encryption key provided!", 400) from e
        return decoded_key


    def _decode_from_bytes(self, key: bytes) -> bytes:
        return b64decode(key)


    def _encrypt_flutterwave_data_with_aes(
        self, data: dict | str | Any, nonce: str | None = None,
        cipher: AESGCM | None = None
    ) -> dict[str, str] | str | Any:
        """encrypts data with AES algorithm according to flutterwave requirements"""
        if not nonce:
            nonce = self.generate_nonce(length=12)

        nonce_bytes: bytes = nonce.encode()
        cipher = cipher or AESGCM(self.key)

        encrypted_dict_data: dict[str, str | Any] = {}
        if isinstance(data, dict):
            for key, value in data.items():
                encrypted_dict_data[key] = self._encrypt_flutterwave_data_with_aes(
                    value, nonce=nonce, cipher=cipher
                )
            encrypted_dict_data["nonce"] = nonce
            return encrypted_dict_data

        if isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)
        data_bytes = data_str.encode()
        encrypted_data = cipher.encrypt(nonce_bytes, data_bytes, None)
        encrypted_data_b64 = b64encode(encrypted_data).decode()
        return encrypted_data_b64


    def generate_nonce(self, length: int = 12) -> str:
        """
        generates random string of given length to be used as nonce for encryption
        """
        chars = string.ascii_letters + string.digits
        nonce = "".join(secrets.choice(chars) for _ in range(length))
        return nonce
