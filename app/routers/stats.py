from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.database import get_db
from app.models import Student
from app.schemas import DashboardStatsResponse
import app.crud as crud

router = APIRouter(prefix="/stats", tags=["Dashboard Statistics"])

@router.get(
    "",
    response_model=DashboardStatsResponse,
    summary="Retrieve real-time dashboard statistics",
    description="Returns metrics calculated directly from database records: total students, distinct courses, recent enrollments, and course distribution."
)
def get_stats_endpoint(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db=db)

@router.get(
    "/courses",
    response_model=List[str],
    summary="List all distinct courses currently in the database"
)
def get_courses_list_endpoint(db: Session = Depends(get_db)):
    rows = (
        db.query(distinct(Student.course))
        .filter(Student.course.isnot(None), Student.course != "")
        .order_by(Student.course.asc())
        .all()
    )
    return [r[0] for r in rows if r[0]]
