from src.auth.security import hash_password, verify_password


def test_hash_and_verify_password_roundtrip():
    # Arrange
    pwd = "S3cureP@ssw0rd!"
    # Act
    hashed = hash_password(pwd)
    # Assert
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False
