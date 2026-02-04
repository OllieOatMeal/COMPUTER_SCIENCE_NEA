"""
Initial Encryption Utility Script
Purpose: Test script for encrypting initial user credentials
Used to generate encrypted values for test user accounts
NOTE: This is a utility script
"""

import json
import os
import base64


class EncryptionService:
    """Encryption service for securing user data"""
    def __init__(self):
        self.key = None
        self.get_key()  # Load key immediately on init

    def get_key(self):
        """Retrieve encryption key from environment variables"""
        key = os.getenv("CSNEA_KEY")
        if key is None:
            raise ValueError("Encryption key not found in environment variables.")
        self.key = key

    def _xor_process(self, data):
        """Apply XOR operation to data using the encryption key"""
        result = bytearray()

        for i in range(len(data)):
            key_char = self.key[i % len(self.key)]
            result.append(data[i] ^ ord(key_char))

        return bytes(result)

    def encrypt(self, plaintext):
        """Encrypt plaintext using XOR cipher with salt"""
        salt = os.urandom(8)
        data = salt + plaintext.encode('utf-8')

        encrypted_bytes = self._xor_process(data)
        encoded = base64.b64encode(encrypted_bytes)

        return encoded.decode('utf-8')

    def decrypt(self, ciphertext):
        """Decrypt Base64 encoded ciphertext"""
        encrypted_bytes = base64.b64decode(ciphertext)
        decrypted_data = self._xor_process(encrypted_bytes)

        plaintext_bytes = decrypted_data[8:]
        return plaintext_bytes.decode('utf-8')


# TEST ENCRYPTION
if __name__ == "__main__":
    Protection = EncryptionService()
    print(Protection.encrypt("admin"))
