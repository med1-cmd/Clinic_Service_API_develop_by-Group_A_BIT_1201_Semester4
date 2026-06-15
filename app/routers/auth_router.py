from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.constants import Roles
from app.database import get_db
from app.deps import require_admin
from app.models import User
from app.schemas import UserCreate, AdminCreate, LoginSchema
from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", status_code=201, summary="Public: Register a new user")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    if user.role == Roles.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot register admin account via public endpoint"
        )

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User registered successfully"
    }


@router.post("/register-admin", status_code=201, summary="Admin only: Register a new admin")
def register_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin())
):

    existing_user = db.query(User).filter(
        User.email == admin.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        full_name=admin.full_name,
        email=admin.email,
        password=hash_password(admin.password),
        role=Roles.ADMIN,
        license_number=admin.license_number
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "Admin user registered successfully"
    }


@router.post("/login", summary="Public: Login and receive a JWT access token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm provides username and password
    # We use username as email
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.lower() if isinstance(user.role, str) else user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }