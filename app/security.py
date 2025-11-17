from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def _truncate_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    print(f"Original length (bytes): {len(password_bytes)}")

    if len(password_bytes) <= 72:
        print("No Truncation needed!")
        return password
    truncated_bytes = password_bytes[:72]
    truncated_str = truncated_bytes.decode('utf-8', errors='ignore')
    print(f"Truncated length (bytes): {len(truncated_bytes)}")
    print(f"Truncated password: {truncated_str}")
    return truncated_str

def hash_password(password: str) -> str:
    truncated_password = _truncate_password(password)
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated_password = _truncate_password(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)
