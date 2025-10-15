"""Encryption utilities for secure session storage."""
import base64
import json
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.exceptions import SessionError


class SessionEncryption:
    """Handles encryption and decryption of session data.
    
    Uses Fernet symmetric encryption with a user-provided key.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize encryption with a key.
        
        Args:
            encryption_key: Hex-encoded encryption key (64 characters)
                           If None, encryption will be disabled
        """
        self.encryption_key = encryption_key
        self._fernet: Optional[Fernet] = None
        
        if encryption_key:
            self._initialize_fernet()
    
    def _initialize_fernet(self) -> None:
        """Initialize Fernet cipher with the provided key."""
        try:
            # Validate key format
            if not self.encryption_key or len(self.encryption_key) != 64:
                raise SessionError(
                    "Encryption key must be 64 characters (32 bytes hex-encoded). "
                    f"Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            
            # Convert hex key to bytes
            key_bytes = bytes.fromhex(self.encryption_key)
            
            # Derive a Fernet-compatible key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'linkedin-cv-salt',  # Static salt for deterministic key derivation
                iterations=100000,
            )
            derived_key = kdf.derive(key_bytes)
            fernet_key = base64.urlsafe_b64encode(derived_key)
            
            self._fernet = Fernet(fernet_key)
            
        except ValueError as e:
            raise SessionError(f"Invalid encryption key format: {str(e)}")
        except Exception as e:
            raise SessionError(f"Failed to initialize encryption: {str(e)}")
    
    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt session data.
        
        Args:
            data: Dictionary of session data to encrypt
            
        Returns:
            Encrypted data as bytes
            
        Raises:
            SessionError: If encryption fails or is not enabled
        """
        if not self._fernet:
            raise SessionError("Encryption is not enabled. Provide an encryption key.")
        
        try:
            # Serialize data to JSON
            json_data = json.dumps(data, indent=2)
            json_bytes = json_data.encode('utf-8')
            
            # Encrypt
            encrypted = self._fernet.encrypt(json_bytes)
            return encrypted
            
        except Exception as e:
            raise SessionError(f"Failed to encrypt session data: {str(e)}")
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt session data.
        
        Args:
            encrypted_data: Encrypted data as bytes
            
        Returns:
            Decrypted session data as dictionary
            
        Raises:
            SessionError: If decryption fails or is not enabled
        """
        if not self._fernet:
            raise SessionError("Encryption is not enabled. Provide an encryption key.")
        
        try:
            # Decrypt
            decrypted_bytes = self._fernet.decrypt(encrypted_data)
            
            # Deserialize from JSON
            json_data = decrypted_bytes.decode('utf-8')
            data = json.loads(json_data)
            return data
            
        except InvalidToken:
            raise SessionError(
                "Failed to decrypt session data: Invalid encryption key or corrupted data. "
                "The encryption key may have changed."
            )
        except Exception as e:
            raise SessionError(f"Failed to decrypt session data: {str(e)}")
    
    def encrypt_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Encrypt and save session data to a file.
        
        Args:
            file_path: Path to save encrypted data
            data: Session data to encrypt and save
            
        Raises:
            SessionError: If encryption or file operations fail
        """
        try:
            encrypted = self.encrypt_data(data)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write encrypted data
            file_path.write_bytes(encrypted)
            
            # Set restrictive permissions (owner read/write only)
            file_path.chmod(0o600)
            
        except SessionError:
            raise
        except Exception as e:
            raise SessionError(f"Failed to save encrypted session to {file_path}: {str(e)}")
    
    def decrypt_file(self, file_path: Path) -> Dict[str, Any]:
        """Read and decrypt session data from a file.
        
        Args:
            file_path: Path to encrypted session file
            
        Returns:
            Decrypted session data
            
        Raises:
            SessionError: If decryption or file operations fail
        """
        try:
            if not file_path.exists():
                raise SessionError(f"Session file not found: {file_path}")
            
            # Read encrypted data
            encrypted = file_path.read_bytes()
            
            # Decrypt
            data = self.decrypt_data(encrypted)
            return data
            
        except SessionError:
            raise
        except Exception as e:
            raise SessionError(f"Failed to load encrypted session from {file_path}: {str(e)}")
    
    @staticmethod
    def is_encrypted_file(file_path: Path) -> bool:
        """Check if a file contains encrypted data.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file appears to be encrypted (binary data)
        """
        try:
            if not file_path.exists():
                return False
            
            # Try to parse as JSON - if it fails, it's likely encrypted
            try:
                content = file_path.read_text()
                json.loads(content)
                # Successfully parsed as JSON, so it's plain text
                return False
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not valid JSON or contains binary data, likely encrypted
                return True
                
        except Exception:
            return False


def generate_encryption_key() -> str:
    """Generate a secure random encryption key.
    
    Returns:
        64-character hex-encoded encryption key
    """
    return secrets.token_hex(32)


def save_session(
    session_data: Dict[str, Any],
    file_path: Path,
    encryption_key: Optional[str] = None
) -> None:
    """Save session data, optionally encrypted.
    
    Args:
        session_data: Session data to save
        file_path: Path to save session
        encryption_key: Optional encryption key for secure storage
    """
    if encryption_key:
        # Encrypted save
        encryptor = SessionEncryption(encryption_key)
        encryptor.encrypt_file(file_path, session_data)
    else:
        # Plain JSON save
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(session_data, indent=2))
        file_path.chmod(0o600)


def load_session(
    file_path: Path,
    encryption_key: Optional[str] = None
) -> Dict[str, Any]:
    """Load session data, handling both encrypted and plain formats.
    
    Args:
        file_path: Path to session file
        encryption_key: Optional encryption key for encrypted sessions
        
    Returns:
        Session data dictionary
    """
    if not file_path.exists():
        raise SessionError(f"Session file not found: {file_path}")
    
    # Check if file is encrypted
    is_encrypted = SessionEncryption.is_encrypted_file(file_path)
    
    if is_encrypted:
        if not encryption_key:
            raise SessionError(
                "Session file is encrypted but no encryption key provided. "
                "Set ENCRYPTION_KEY in your .env file."
            )
        encryptor = SessionEncryption(encryption_key)
        return encryptor.decrypt_file(file_path)
    else:
        # Plain JSON file
        return json.loads(file_path.read_text())
