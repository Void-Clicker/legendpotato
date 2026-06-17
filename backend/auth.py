from passlib.context import CryptContext

# Configure bcrypt to handle longer passwords safely
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12,          # Good security
    truncate_error=False        # This helps with the error
)

def hash_password(password: str) -> str:
    # Truncate to 72 characters (bcrypt limit)
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)
