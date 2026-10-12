import re
from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, model_validator

PHONE_REGEX = re.compile(r"^[0-9+\-\s().]{7,25}$")

def normalize_empty_string(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = v.strip()
    return s if s else None

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full student name")
    dob: date = Field(..., description="Date of birth in YYYY-MM-DD format")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Valid email address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    course: Optional[str] = Field(None, max_length=100, description="Course or department name")
    address: Optional[str] = Field(None, max_length=255, description="Residential address")
    enrollment_date: Optional[date] = Field(None, description="Date of enrollment in YYYY-MM-DD format")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Student name cannot be empty or solely whitespace.")
        if len(s) > 100:
            raise ValueError("Student name cannot exceed 100 characters.")
        return s

    @field_validator("course", "address", mode="before")
    @classmethod
    def clean_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        return normalize_empty_string(v)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        cleaned = normalize_empty_string(v)
        if cleaned is not None:
            if not PHONE_REGEX.match(cleaned):
                raise ValueError("Phone number must contain between 7 and 25 valid phone characters (+, -, digits, spaces, parentheses).")
        return cleaned

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: Optional[str]) -> Optional[str]:
        return normalize_empty_string(v)

class StudentCreate(StudentBase):
    @model_validator(mode="after")
    def validate_at_least_one_contact(self) -> "StudentCreate":
        if not self.email and not self.phone:
            raise ValueError("At least one contact method (email or phone) must be provided.")
        return self

class StudentUpdate(StudentBase):
    """Complete replacement payload for PUT requests."""
    @model_validator(mode="after")
    def validate_at_least_one_contact(self) -> "StudentUpdate":
        if not self.email and not self.phone:
            raise ValueError("At least one contact method (email or phone) must be provided.")
        return self

class StudentPatch(BaseModel):
    """Partial update payload for PATCH requests."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    dob: Optional[date] = None
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def validate_patch_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            s = v.strip()
            if not s:
                raise ValueError("Student name cannot be empty or solely whitespace.")
            return s
        return v

    @field_validator("course", "address", mode="before")
    @classmethod
    def clean_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        return normalize_empty_string(v)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        cleaned = normalize_empty_string(v)
        if cleaned is not None:
            if not PHONE_REGEX.match(cleaned):
                raise ValueError("Phone number must contain between 7 and 25 valid phone characters.")
        return cleaned

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: Optional[str]) -> Optional[str]:
        return normalize_empty_string(v)

class StudentResponse(BaseModel):
    student_id: int
    name: str
    dob: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedStudentsResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[StudentResponse]

class CourseCount(BaseModel):
    course: str
    count: int

class DashboardStatsResponse(BaseModel):
    total_students: int
    total_courses: int
    recent_enrollments: List[StudentResponse]
    course_distribution: List[CourseCount]

class AIQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=300, description="Natural language question about student records")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Question cannot be empty.")
        return s

class AIResponse(BaseModel):
    question: str
    answer: str
    source: str
    data_summary: Optional[Dict] = None
