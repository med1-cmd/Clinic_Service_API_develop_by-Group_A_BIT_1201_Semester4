from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate, ReviewOut
from app.deps import require_patient, require_admin


router = APIRouter(
	prefix="/reviews",
	tags=["Reviews"]
)


@router.post("/", status_code=201, response_model=ReviewOut, summary="Create a review (authenticated patients)")
def create_review(review: ReviewCreate, db: Session = Depends(get_db), user=Depends(require_patient())):
	payload = review.model_dump()
	payload["user_id"] = user.get("id")
	new = Review(**payload)
	db.add(new)
	db.commit()
	db.refresh(new)
	return new


@router.get("/", response_model=list[ReviewOut], summary="List all reviews")
def list_reviews(db: Session = Depends(get_db)):
	return db.query(Review).all()


@router.get("/clinic/{clinic_id}", response_model=list[ReviewOut], summary="List reviews for a clinic")
def reviews_for_clinic(clinic_id: int, db: Session = Depends(get_db)):
	return db.query(Review).filter(Review.clinic_id == clinic_id).all()


@router.get("/{review_id}", response_model=ReviewOut, summary="Get review by id")
def get_review(review_id: int, db: Session = Depends(get_db)):
	rv = db.query(Review).filter(Review.id == review_id).first()
	if not rv:
		raise HTTPException(status_code=404, detail="Review not found")
	return rv


@router.patch("/{review_id}", response_model=ReviewOut, summary="Update a review (owner or admin)")
def update_review(review_id: int, review_update: ReviewUpdate, db: Session = Depends(get_db), user=Depends(require_patient())):
	rv = db.query(Review).filter(Review.id == review_id).first()
	if not rv:
		raise HTTPException(status_code=404, detail="Review not found")
	# allow owner or admin
	if rv.user_id != user.get("id"):
		# check if admin
		if user.get("role") != "admin":
			raise HTTPException(status_code=403, detail="Not allowed to modify this review")
	data = review_update.model_dump(exclude_unset=True)
	for k, v in data.items():
		setattr(rv, k, v)
	db.commit()
	db.refresh(rv)
	return rv


@router.delete("/{review_id}", summary="Admin only: Delete a review")
def delete_review(review_id: int, db: Session = Depends(get_db), user=Depends(require_admin())):
	rv = db.query(Review).filter(Review.id == review_id).first()
	if not rv:
		raise HTTPException(status_code=404, detail="Review not found")
	db.delete(rv)
	db.commit()
	return {"message": "Review deleted"}

