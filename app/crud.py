from typing import Optional, Tuple, List, Dict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from fastapi import HTTPException, status
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentPatch

def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Retrieve a single student by primary key."""
    return db.query(Student).filter(Student.student_id == student_id).first()

def get_students(
    db: Session,
    search: Optional[str] = None,
    course: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[Student], int]:
    """Retrieve students with optional search, course filter, and pagination."""
    query = db.query(Student)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(Student.name.ilike(search_term))

    if course:
        course_clean = course.strip()
        if course_clean:
            query = query.filter(Student.course == course_clean)

    total = query.count()
    items = query.order_by(Student.student_id.desc()).offset(skip).limit(limit).all()
    return items, total

def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create a new student record."""
    student_data = student_in.model_dump()
    db_student = Student(**student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student: Student, update_in: StudentUpdate) -> Student:
    """Completely replace editable fields of an existing student."""
    update_data = update_in.model_dump()
    for field, value in update_data.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student

def patch_student(db: Session, student: Student, patch_in: StudentPatch) -> Student:
    """Partially update an existing student and validate the final merged state."""
    patch_data = patch_in.model_dump(exclude_unset=True)

    # Determine resulting fields
    resulting_email = patch_data.get("email", student.email)
    resulting_phone = patch_data.get("phone", student.phone)

    # Clean empty strings if any
    if resulting_email is not None and not str(resulting_email).strip():
        resulting_email = None
    if resulting_phone is not None and not str(resulting_phone).strip():
        resulting_phone = None

    if not resulting_email and not resulting_phone:
        raise HTTPException(
            status_code=422,
            detail="Student must retain at least one valid contact method (email or phone)."
        )

    for field, value in patch_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student: Student) -> None:
    """Delete a student record."""
    db.delete(student)
    db.commit()

def get_dashboard_stats(db: Session) -> Dict:
    """Calculate aggregated metrics directly from database."""
    total_students = db.query(func.count(Student.student_id)).scalar() or 0

    total_courses = db.query(
        func.count(func.distinct(Student.course))
    ).filter(
        Student.course.isnot(None),
        Student.course != ""
    ).scalar() or 0

    # Recent enrollments
    recent_students = (
        db.query(Student)
        .order_by(
            Student.enrollment_date.desc().nullslast(),
            Student.student_id.desc()
        )
        .limit(5)
        .all()
    )

    # Course distribution
    distribution_query = (
        db.query(
            Student.course,
            func.count(Student.student_id).label("count")
        )
        .group_by(Student.course)
        .order_by(desc("count"))
        .all()
    )

    course_distribution = []
    for course_name, count in distribution_query:
        course_distribution.append({
            "course": course_name if course_name else "Unassigned",
            "count": count
        })

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "recent_enrollments": recent_students,
        "course_distribution": course_distribution
    }

def seed_sample_students_if_empty(db: Session) -> None:
    """Seed initial fictional academic records if the database is currently empty."""
    if db.query(Student).count() > 0:
        return

    sample_data = [
        {
            "name": "Aarav Sharma",
            "dob": date(2002, 5, 14),
            "email": "aarav.sharma@ewbedutech.org",
            "phone": "+91 98765 43210",
            "course": "Artificial Intelligence",
            "address": "42 Tech Residency, Bangalore, Karnataka",
            "enrollment_date": date(2024, 7, 15)
        },
        {
            "name": "Priya Nair",
            "dob": date(2003, 11, 20),
            "email": "priya.nair@ewbedutech.org",
            "phone": "+91 98765 43211",
            "course": "Computer Science",
            "address": "18 Marine Drive, Kochi, Kerala",
            "enrollment_date": date(2024, 7, 16)
        },
        {
            "name": "Rohan Deshmukh",
            "dob": date(2001, 8, 9),
            "email": "rohan.deshmukh@ewbedutech.org",
            "phone": "+91 98765 43212",
            "course": "Data Science",
            "address": "7 Green Avenue, Pune, Maharashtra",
            "enrollment_date": date(2024, 8, 1)
        },
        {
            "name": "Sneha Kulkarni",
            "dob": date(2002, 3, 27),
            "email": "sneha.kulkarni@ewbedutech.org",
            "phone": "+91 98765 43213",
            "course": "Cybersecurity",
            "address": "104 Pearl Heights, Hyderabad, Telangana",
            "enrollment_date": date(2024, 8, 10)
        },
        {
            "name": "Vikramaditya Verma",
            "dob": date(2001, 12, 3),
            "email": "vikram.verma@ewbedutech.org",
            "phone": "+91 98765 43214",
            "course": "Cloud Computing",
            "address": "88 Civil Lines, Jaipur, Rajasthan",
            "enrollment_date": date(2024, 8, 15)
        },
        {
            "name": "Ananya Sen",
            "dob": date(2003, 6, 18),
            "email": "ananya.sen@ewbedutech.org",
            "phone": "+91 98765 43215",
            "course": "Artificial Intelligence",
            "address": "15 Park Street, Kolkata, West Bengal",
            "enrollment_date": date(2024, 9, 1)
        },
        {
            "name": "Kabir Patel",
            "dob": date(2002, 9, 30),
            "email": "kabir.patel@ewbedutech.org",
            "phone": "+91 98765 43216",
            "course": "Computer Science",
            "address": "23 Riverfront, Ahmedabad, Gujarat",
            "enrollment_date": date(2024, 9, 5)
        },
        {
            "name": "Meera Iyer",
            "dob": date(2003, 1, 12),
            "email": "meera.iyer@ewbedutech.org",
            "phone": "+91 98765 43217",
            "course": "Data Science",
            "address": "66 Temple Bay, Chennai, Tamil Nadu",
            "enrollment_date": date(2024, 9, 12)
        }
    ]

    for item in sample_data:
        db.add(Student(**item))
    db.commit()
