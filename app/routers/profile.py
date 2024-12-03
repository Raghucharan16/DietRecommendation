from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, database

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/profile")
def profile_get(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("profile.html", {"request": request})

@router.post("/profile/update")
def update_profile(request: Request, age: int = Form(...), gender: str = Form(...), weight: float = Form(...), height: float = Form(...), vegan: str = Form(...), output: str = Form(...),exercise_level: str = Form(...), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    user.age = age
    user.gender = gender
    user.weight = weight
    user.height = height
    user.vegan = vegan
    user.output = output
    user.exercise_level = exercise_level
    db.commit()
    return RedirectResponse(url="/recommendations", status_code=303)