from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentPatch,
    StudentResponse,
    PaginatedStudentsResponse,
)
import app.crud as crud
from app.config import settings

router = APIRouter(prefix="/students", tags=["Students"])

@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create student record",
    description="Registers a new student. Requires non-empty name, valid date of birth, and at least one contact method (email or phone)."
)
def create_student_endpoint(
    student_in: StudentCreate,
    db: Session = Depends(get_db)
):
    return crud.create_student(db=db, student_in=student_in)

@router.get(
    "",
    response_model=PaginatedStudentsResponse,
    summary="List, search, filter, and paginate students",
    description="Returns a paginated list of students. Supports case-insensitive partial-name search and exact course filtering."
)
def list_students_endpoint(
    search: Optional[str] = Query(None, description="Case-insensitive partial-name search"),
    course: Optional[str] = Query(None, description="Course filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Max records to return (capped at 100)"),
    db: Session = Depends(get_db)
):
    items, total = crud.get_students(
        db=db,
        search=search,
        course=course,
        skip=skip,
        limit=limit
    )
    return PaginatedStudentsResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items
    )

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Retrieve one student by ID",
    description="Fetches a single student record by their primary key ID. Returns 404 if the student does not exist."
)
def get_student_endpoint(
    student_id: int = Path(..., ge=1, description="Student ID primary key"),
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return student

@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Replace editable student details",
    description="Completely replaces all editable fields of an existing student. The student's primary key ID cannot be modified."
)
def update_student_endpoint(
    student_id: int = Path(..., ge=1, description="Student ID primary key"),
    update_in: StudentUpdate = ...,
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return crud.update_student(db=db, student=student, update_in=update_in)

@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Partially update student fields",
    description="Updates only the supplied fields for the given student. Preserves all omitted fields and validates the resulting record."
)
def patch_student_endpoint(
    student_id: int = Path(..., ge=1, description="Student ID primary key"),
    patch_in: StudentPatch = ...,
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return crud.patch_student(db=db, student=student, patch_in=patch_in)

@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete student record",
    description="Permanently deletes a student record. Repeated deletion of a non-existent record returns HTTP 404."
)
def delete_student_endpoint(
    student_id: int = Path(..., ge=1, description="Student ID primary key"),
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    crud.delete_student(db=db, student=student)
    return None
