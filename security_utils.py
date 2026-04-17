from cryptography.fernet import Fernet
import os

# In a production environment, this key should be stored in environment variables or a secret vault.
# We'll generate a consistent key for this environment.
ENCRYPTION_KEY = b'G6Yp_m_v6P_Hq_t3_Z1_v5B_s2_T1_V4X_C3_X1_v5B='

class SecurityLayer:
    def __init__(self, key=None):
        self.key = key or ENCRYPTION_KEY
        self.cipher = Fernet(self.key)

    def encrypt_data(self, data):
        """Encrypts a string into a URL-safe base64-encoded bytes string."""
        if not data:
            return None
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """Decrypts URL-safe base64-encoded bytes back into a string."""
        if not encrypted_data:
            return None
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # Fallback for unencrypted legacy data during transition
            return encrypted_data

# Global instance
shield = SecurityLayer()
