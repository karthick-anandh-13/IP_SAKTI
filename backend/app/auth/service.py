"""
Auth business logic: password hashing/verification and user persistence.

Uses the `bcrypt` library directly rather than passlib's CryptContext:
recent bcrypt (>=4.1) releases changed internals in a way that breaks
passlib's backend self-test, so calling bcrypt directly avoids that whole
fragile interaction.
"""
import bcrypt
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserRegister

_BCRYPT_MAX_BYTES = 72  # bcrypt silently ignores/rejects anything beyond this


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))
    except ValueError:
        return False


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, payload: UserRegister) -> User:
    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
