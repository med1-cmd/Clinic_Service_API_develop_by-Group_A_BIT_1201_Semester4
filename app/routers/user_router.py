from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserOut, UserUpdate
from app.deps import require_admin

router = APIRouter(
    prefix="/users",
    tags=["User Management"]
)


@router.get("/", response_model=list[UserOut], summary="Admin only: List all users in the system")
def get_users(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: List all users in the system"""
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut, summary="Admin only: Get specific user details")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Get specific user details"""
    user_obj = db.query(User).filter(User.id == user_id).first()
    
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_obj


@router.patch("/{user_id}", response_model=UserOut, summary="Admin only: Update user details")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Update user details"""
    user_obj = db.query(User).filter(User.id == user_id).first()
    
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_obj, key, value)
    
    db.commit()
    db.refresh(user_obj)
    
    return user_obj


@router.delete("/{user_id}", summary="Admin only: Delete a user")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Delete a user"""
    user_obj = db.query(User).filter(User.id == user_id).first()
    
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user_obj)
    db.commit()
    
    return {"message": "User deleted successfully"}
