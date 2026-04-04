"""

ENV KEY Oliver02092007

"""


"""

# Code to encrypt/ decrypt data

"""

"""
# Import nessicary functions/ procedures
"""
import json
import os
import base64


class EncryptionService:
    def __init__(self):
        self._key = None
        self.get_key()

    # Gets the environmental key stored on the computer
    def get_key(self):
        key = os.getenv("CSNEA_KEY")
        if key is None:
            raise ValueError("Encryption key not found in environment variables.")
        self._key = key

    # Encrypts the data
    def _xor_process(self, data):
        result = bytearray()
        for i in range(len(data)):
            key_char = self._key[i % len(self._key)]
            result.append(data[i] ^ ord(key_char))
        return bytes(result)

    # Encrypts the data
    def encrypt(self, plaintext):
        salt = os.urandom(8)
        data = salt + plaintext.encode('utf-8')

        encrypted_bytes = self._xor_process(data)
        
        encoded = base64.b64encode(encrypted_bytes)

        return encoded.decode('utf-8')

    # Places the data in base 64 from plaintext
    def encrypt_deterministic(self, plaintext):
        data = plaintext.encode('utf-8')
        encrypted_bytes = self._xor_process(data)
        encoded = base64.b64encode(encrypted_bytes)
        return encoded.decode('utf-8')

    # Places the data in plaintext from base 64
    def decrypt_deterministic(self, ciphertext):
        encrypted_bytes = base64.b64decode(ciphertext)
        decrypted_bytes = self._xor_process(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')

    # Decrypts the data
    def decrypt(self, ciphertext):
        encrypted_bytes = base64.b64decode(ciphertext)
        
        decrypted_data = self._xor_process(encrypted_bytes)

        plaintext_bytes = decrypted_data[8:]
        return plaintext_bytes.decode('utf-8')
