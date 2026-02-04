"""
Encryption tool I use to test encrypting and decrypting data
Useful for testing how the encryption works before putting stuff in the database
"""

import json
import os
import base64


class EncryptionService:
    """Handles all the encryption and decryption using XOR cipher"""
    def __init__(self):
        self.key = None
        self.get_key()  # Load key immediately on init

    def get_key(self):
        """Gets the encryption key from the environment variable CSNEA_KEY"""
        key = os.getenv("CSNEA_KEY")
        if key is None:
            raise ValueError("Encryption key not found in environment variables.")
        self.key = key

    def _xor_process(self, data):
        """Does the XOR encryption/decryption on the data"""
        result = bytearray()

        for i in range(len(data)):
            key_char = self.key[i % len(self.key)]
            result.append(data[i] ^ ord(key_char))

        return bytes(result)

    def encrypt(self, plaintext):
        """Takes plain text and turns it into encrypted gibberish that can't be read"""
        salt = os.urandom(8)
        data = salt + plaintext.encode('utf-8')

        encrypted_bytes = self._xor_process(data)
        encoded = base64.b64encode(encrypted_bytes)

        return encoded.decode('utf-8')

    def decrypt(self, ciphertext):
        """Takes the encrypted text and converts it back to readable plain text"""
        encrypted_bytes = base64.b64decode(ciphertext)
        decrypted_data = self._xor_process(encrypted_bytes)

        plaintext_bytes = decrypted_data[8:]
        return plaintext_bytes.decode('utf-8')


# Test it out
if __name__ == "__main__":
    Protection = EncryptionService()
    print(Protection.encrypt("admin"))
