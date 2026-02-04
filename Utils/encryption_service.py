"""
Encryption Service Module
Purpose: Provides XOR-based encryption and decryption with Base64 encoding
Uses a key from environment variables for secure data protection
"""

import json
import os
import base64


class EncryptionService:
    """
    Encryption service for securing user data
    Implements XOR cipher with salt and Base64 encoding
    """

    def __init__(self):
        """Initialise the encryption service and load the key from environment"""
        self.key = None
        self.get_key()  # Load key immediately on init

    def get_key(self):
        """
        Retrieve encryption key from environment variables
        Raises ValueError if key is not found
        """
        key = os.getenv("CSNEA_KEY")
        if key is None:
            raise ValueError("Encryption key not found in environment variables.")
        self.key = key

    def _xor_process(self, data):
        """
        Apply XOR operation to data using the encryption key
        Args: data (bytes) - data to encrypt/decrypt
        Returns: bytes - XOR processed data
        """
        result = bytearray()

        # XOR each byte with corresponding key character
        for i in range(len(data)):
            key_char = self.key[i % len(self.key)]
            result.append(data[i] ^ ord(key_char))

        return bytes(result)

    def encrypt(self, plaintext):
        """
        Encrypt plaintext using XOR cipher with salt
        Args: plaintext (str) - text to encrypt
        Returns: str - Base64 encoded encrypted data
        """
        # Generate random 8-byte salt for added security
        salt = os.urandom(8)
        data = salt + plaintext.encode('utf-8')

        # Apply XOR encryption
        encrypted_bytes = self._xor_process(data)
        
        # Encode to Base64 for safe transmission/storage
        encoded = base64.b64encode(encrypted_bytes)

        return encoded.decode('utf-8')

    def decrypt(self, ciphertext):
        """
        Decrypt Base64 encoded ciphertext
        Args: ciphertext (str) - Base64 encoded encrypted data
        Returns: str - decrypted plaintext
        """
        # Decode from Base64
        encrypted_bytes = base64.b64decode(ciphertext)
        
        # Apply XOR decryption
        decrypted_data = self._xor_process(encrypted_bytes)

        # Remove salt (first 8 bytes) and decode to UTF-8
        plaintext_bytes = decrypted_data[8:]
        return plaintext_bytes.decode('utf-8')
