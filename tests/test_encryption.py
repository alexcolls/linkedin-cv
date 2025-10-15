"""Tests for encryption utilities."""
import json
import tempfile
from pathlib import Path

import pytest

from src.exceptions import SessionError
from src.utils.encryption import (
    SessionEncryption,
    generate_encryption_key,
    load_session,
    save_session,
)


class TestSessionEncryption:
    """Test session encryption and decryption."""
    
    def test_generate_key(self):
        """Test encryption key generation."""
        key = generate_encryption_key()
        
        assert isinstance(key, str)
        assert len(key) == 64  # 32 bytes hex-encoded
        
        # Generate another key and ensure they're different
        key2 = generate_encryption_key()
        assert key != key2
    
    def test_initialization_with_valid_key(self):
        """Test initializing encryption with valid key."""
        key = generate_encryption_key()
        encryptor = SessionEncryption(key)
        
        assert encryptor.encryption_key == key
        assert encryptor._fernet is not None
    
    def test_initialization_without_key(self):
        """Test initializing without encryption key."""
        encryptor = SessionEncryption(None)
        
        assert encryptor.encryption_key is None
        assert encryptor._fernet is None
    
    def test_initialization_with_invalid_key_length(self):
        """Test error on invalid key length."""
        with pytest.raises(SessionError) as exc_info:
            SessionEncryption("short_key")
        
        assert "must be 64 characters" in str(exc_info.value)
    
    def test_initialization_with_invalid_key_format(self):
        """Test error on invalid hex format."""
        invalid_key = "z" * 64  # Not valid hex
        
        with pytest.raises(SessionError) as exc_info:
            SessionEncryption(invalid_key)
        
        assert "Invalid encryption key format" in str(exc_info.value)
    
    def test_encrypt_decrypt_data(self):
        """Test basic encryption and decryption."""
        key = generate_encryption_key()
        encryptor = SessionEncryption(key)
        
        test_data = {
            "cookies": [{"name": "session", "value": "abc123"}],
            "user": "testuser",
            "timestamp": "2024-01-01"
        }
        
        # Encrypt
        encrypted = encryptor.encrypt_data(test_data)
        assert isinstance(encrypted, bytes)
        assert encrypted != json.dumps(test_data).encode()
        
        # Decrypt
        decrypted = encryptor.decrypt_data(encrypted)
        assert decrypted == test_data
    
    def test_encrypt_without_key(self):
        """Test error when encrypting without key."""
        encryptor = SessionEncryption(None)
        
        with pytest.raises(SessionError) as exc_info:
            encryptor.encrypt_data({"test": "data"})
        
        assert "not enabled" in str(exc_info.value)
    
    def test_decrypt_with_wrong_key(self):
        """Test error when decrypting with wrong key."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        
        encryptor1 = SessionEncryption(key1)
        encryptor2 = SessionEncryption(key2)
        
        test_data = {"secret": "value"}
        encrypted = encryptor1.encrypt_data(test_data)
        
        with pytest.raises(SessionError) as exc_info:
            encryptor2.decrypt_data(encrypted)
        
        assert "Invalid encryption key" in str(exc_info.value)
    
    def test_encrypt_decrypt_file(self):
        """Test encrypting and decrypting files."""
        key = generate_encryption_key()
        encryptor = SessionEncryption(key)
        
        test_data = {
            "session_id": "12345",
            "cookies": [{"name": "auth", "value": "token"}]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "session.enc"
            
            # Encrypt and save
            encryptor.encrypt_file(file_path, test_data)
            
            assert file_path.exists()
            assert file_path.stat().st_mode & 0o777 == 0o600  # Check permissions
            
            # Read and decrypt
            decrypted = encryptor.decrypt_file(file_path)
            assert decrypted == test_data
    
    def test_is_encrypted_file(self):
        """Test detecting encrypted files."""
        key = generate_encryption_key()
        encryptor = SessionEncryption(key)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create encrypted file
            encrypted_path = Path(tmpdir) / "encrypted.dat"
            encryptor.encrypt_file(encrypted_path, {"test": "data"})
            
            # Create plain JSON file
            plain_path = Path(tmpdir) / "plain.json"
            plain_path.write_text(json.dumps({"test": "data"}))
            
            assert SessionEncryption.is_encrypted_file(encrypted_path) is True
            assert SessionEncryption.is_encrypted_file(plain_path) is False
            assert SessionEncryption.is_encrypted_file(Path(tmpdir) / "nonexistent") is False


class TestSaveLoadSession:
    """Test high-level session save/load functions."""
    
    def test_save_and_load_encrypted_session(self):
        """Test saving and loading encrypted session."""
        key = generate_encryption_key()
        
        session_data = {
            "cookies": [{"name": "session", "value": "abc123"}],
            "profile": {"user": "testuser"}
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "session.enc"
            
            # Save encrypted
            save_session(session_data, file_path, encryption_key=key)
            
            # Load encrypted
            loaded = load_session(file_path, encryption_key=key)
            assert loaded == session_data
    
    def test_save_and_load_plain_session(self):
        """Test saving and loading plain (unencrypted) session."""
        session_data = {
            "cookies": [{"name": "session", "value": "abc123"}]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "session.json"
            
            # Save plain
            save_session(session_data, file_path, encryption_key=None)
            
            # Verify it's plain JSON
            assert json.loads(file_path.read_text()) == session_data
            
            # Load plain
            loaded = load_session(file_path, encryption_key=None)
            assert loaded == session_data
    
    def test_load_encrypted_without_key(self):
        """Test error when loading encrypted file without key."""
        key = generate_encryption_key()
        session_data = {"test": "data"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "session.enc"
            save_session(session_data, file_path, encryption_key=key)
            
            # Try to load without key
            with pytest.raises(SessionError) as exc_info:
                load_session(file_path, encryption_key=None)
            
            assert "encrypted but no encryption key provided" in str(exc_info.value)
    
    def test_load_encrypted_with_wrong_key(self):
        """Test error when loading with wrong key."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        
        session_data = {"test": "data"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "session.enc"
            save_session(session_data, file_path, encryption_key=key1)
            
            # Try to load with different key
            with pytest.raises(SessionError) as exc_info:
                load_session(file_path, encryption_key=key2)
            
            assert "Invalid encryption key" in str(exc_info.value)
    
    def test_load_nonexistent_file(self):
        """Test error when loading nonexistent file."""
        with pytest.raises(SessionError) as exc_info:
            load_session(Path("/nonexistent/session.json"))
        
        assert "not found" in str(exc_info.value)
    
    def test_backward_compatibility(self):
        """Test that plain sessions can still be loaded."""
        session_data = {
            "legacy": "session",
            "cookies": []
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate old plain JSON session
            file_path = Path(tmpdir) / "old_session.json"
            file_path.write_text(json.dumps(session_data))
            
            # Should load successfully without encryption key
            loaded = load_session(file_path)
            assert loaded == session_data


class TestEncryptionSecurity:
    """Test security aspects of encryption."""
    
    def test_different_keys_produce_different_ciphertext(self):
        """Test that same data with different keys produces different ciphertext."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        
        encryptor1 = SessionEncryption(key1)
        encryptor2 = SessionEncryption(key2)
        
        test_data = {"secret": "data"}
        
        encrypted1 = encryptor1.encrypt_data(test_data)
        encrypted2 = encryptor2.encrypt_data(test_data)
        
        assert encrypted1 != encrypted2
    
    def test_same_key_produces_different_ciphertext(self):
        """Test that encrypting same data twice produces different ciphertext (IV)."""
        key = generate_encryption_key()
        encryptor = SessionEncryption(key)
        
        test_data = {"secret": "data"}
        
        # Encrypt same data twice
        encrypted1 = encryptor.encrypt_data(test_data)
        encrypted2 = encryptor.encrypt_data(test_data)
        
        # Ciphertext should differ due to different IVs
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same data
        assert encryptor.decrypt_data(encrypted1) == test_data
        assert encryptor.decrypt_data(encrypted2) == test_data
    
    def test_file_permissions(self):
        """Test that encrypted files have secure permissions."""
        key = generate_encryption_key()
        encryptor = SessionEncryption(key)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "secure_session.enc"
            encryptor.encrypt_file(file_path, {"test": "data"})
            
            # Check permissions are 0o600 (owner read/write only)
            mode = file_path.stat().st_mode & 0o777
            assert mode == 0o600
