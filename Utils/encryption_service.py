"""
My encryption service that uses XOR with a key from the environment
Encrypts data using Base64 encoding
"""

import json
import os
import base64


class EncryptionService:
    """Encrypts and decrypts data using XOR cipher with a salt"""

    def __init__(self):
        """Initialize and load the encryption key from environment"""
        # Grab the key right away so this is ready to go
        self.key = None
        self.get_key()  # Load key immediately on init

    def get_key(self):
        """
        Retrieve encryption key from environment variables
        Raises ValueError if key is not found
        """
        # Just read the key from the environment
        key = os.getenv("CSNEA_KEY")
        if key is None:
            raise ValueError("Encryption key not found in environment variables.")
        self.key = key

    def _xor_process(self, data):
        """
        Apply XOR operation to data using the encryption key
        Args: data (bytes) - data to encrypt/decrypt
        Returns: bytes - XOR encrypted/decrypted data
        """
        # Do a simple XOR pass over the bytes
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
        # Salt + XOR + Base64 so it's safe to store
        # Generate random 8-byte salt for added security
        salt = os.urandom(8)
        data = salt + plaintext.encode('utf-8')

        # Apply XOR encryption
        encrypted_bytes = self._xor_process(data)
        
        # Encode to Base64 for safe transmission/storage
        encoded = base64.b64encode(encrypted_bytes)

        return encoded.decode('utf-8')

    def encrypt_deterministic(self, plaintext):
        """
        Deterministic encryption without random salt (for lookup keys like usernames)
        Args: plaintext (str)
        Returns: str - Base64 encoded encrypted data
        """
        # Same input -> same output for lookup fields
        data = plaintext.encode('utf-8')
        encrypted_bytes = self._xor_process(data)
        encoded = base64.b64encode(encrypted_bytes)
        return encoded.decode('utf-8')

    def decrypt_deterministic(self, ciphertext):
        """
        Deterministic decryption for values encrypted without salt
        Args: ciphertext (str) - Base64 encoded encrypted data
        Returns: str - decrypted plaintext
        """
        # Reverse the deterministic XOR + Base64
        encrypted_bytes = base64.b64decode(ciphertext)
        decrypted_bytes = self._xor_process(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')

    def decrypt(self, ciphertext):
        """
        Decrypt Base64 encoded ciphertext
        Args: ciphertext (str) - Base64 encoded encrypted data
        Returns: str - decrypted plaintext
        """
        # Decode, XOR, then drop the salt
        # Decode from Base64
        encrypted_bytes = base64.b64decode(ciphertext)
        
        # Apply XOR decryption
        decrypted_data = self._xor_process(encrypted_bytes)

        # Remove salt (first 8 bytes) and decode to UTF-8
        plaintext_bytes = decrypted_data[8:]
        return plaintext_bytes.decode('utf-8')
