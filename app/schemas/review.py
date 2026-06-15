from pydantic import BaseModel
from .base import NoIdCreateModel, NoIdUpdateModel


class ReviewCreate(NoIdCreateModel):
    clinic_id: int
    rating: int
    comment: str | None = None


class ReviewUpdate(NoIdUpdateModel):
    rating: int | None = None
    comment: str | None = None


class ReviewOut(ReviewCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
