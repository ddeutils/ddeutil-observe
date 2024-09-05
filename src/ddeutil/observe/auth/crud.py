from typing import Optional

from sqlalchemy.orm import Session

from .models import User
from .securities import verify_password


async def authenticate(
    session: Session,
    *,
    email: str,
    password: str,
) -> Optional[User]:
    if user := await User.get_by_email(session, email=email):
        return user if verify_password(password, user.hashed_password) else None
    else:
        return None


def is_active(user: User) -> bool:
    return user.is_active


def is_superuser(user: User) -> bool:
    return user.is_superuser
