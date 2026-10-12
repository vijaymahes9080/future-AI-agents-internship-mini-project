from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    dob = Column(Date, nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Student(student_id={self.student_id}, name='{self.name}', course='{self.course}')>"
