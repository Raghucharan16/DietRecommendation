from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, database
import sys
import os
import importlib.util

# Add the project root to sys.path if not already there
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the updated models
from models import diet_model, exercise_model
import markdown

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recommendations")
def get_recommendations(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    user_data = {
        "age": user.age,
        "gender": user.gender,
        "weight": user.weight,
        "height": user.height,
        "vegan": user.vegan,
        "output": user.output,
        "exercise_level": user.exercise_level
    }

    diet_plan_md = diet_model.generate_diet_plan(user_data)
    exercise_plan_md = exercise_model.generate_exercise_plan(user_data)

    # Debug: Print to console if there are errors
    if diet_plan_md and diet_plan_md.startswith("Error"):
        print(f"Diet Model Error: {diet_plan_md}")
    if exercise_plan_md and exercise_plan_md.startswith("Error"):
        print(f"Exercise Model Error: {exercise_plan_md}")

    diet_plan_html = markdown.markdown(diet_plan_md)
    exercise_plan_html = markdown.markdown(exercise_plan_md)

    return templates.TemplateResponse("recommendations.html", {
        "request": request,
        "diet_plan": diet_plan_html,
        "exercise_plan": exercise_plan_html
    })