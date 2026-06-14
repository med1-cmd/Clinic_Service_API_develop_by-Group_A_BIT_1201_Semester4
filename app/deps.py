from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import get_settings
from app.constants import Roles

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


# Get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        raw_role = payload.get("role")

        return {
            "id": int(payload["sub"]),
            "email": payload.get("email"),
            "role": raw_role.lower() if isinstance(raw_role, str) else raw_role
        }

    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# Role checker (IMPORTANT)
def require_role(required_role: str):
    def checker(user=Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail="Access denied: insufficient permissions"
            )
        return user
    return checker


def require_roles(*required_roles: str):
    def checker(user=Depends(get_current_user)):
        if user.get("role") not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied: insufficient permissions"
            )
        return user
    return checker


def require_admin():
    return require_role(Roles.ADMIN)


def require_doctor():
    return require_role(Roles.DOCTOR)


def require_doctor_or_admin():
    return require_roles(Roles.DOCTOR, Roles.ADMIN)


def require_patient():
    return require_role(Roles.PATIENT)
