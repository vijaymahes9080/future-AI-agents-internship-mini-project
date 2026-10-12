import re
from typing import Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Student
from app.config import settings

def parse_and_retrieve_facts(db: Session, question: str) -> Dict[str, Any]:
    """Safely extracts context and computes exact calculations in Python/ORM."""
    q = question.lower().strip()
    total_count = db.query(func.count(Student.student_id)).scalar() or 0

    facts: Dict[str, Any] = {
        "total_students": total_count,
        "matched_intent": "general_summary"
    }

    if total_count == 0:
        facts["matched_intent"] = "empty_database"
        facts["message"] = "The database currently contains 0 student records."
        return facts

    # Year query check: e.g. "born after 2002" or "born before 2003"
    year_match = re.search(r"born (after|before|in)\s+(\d{4})", q)
    if year_match:
        rel, year_str = year_match.groups()
        year = int(year_str)
        if rel == "after":
            count = db.query(func.count(Student.student_id)).filter(extract("year", Student.dob) > year).scalar() or 0
            matching_students = db.query(Student.name, Student.dob, Student.course).filter(extract("year", Student.dob) > year).all()
            facts["matched_intent"] = "students_by_dob"
            facts["condition"] = f"born after {year}"
            facts["count"] = count
            facts["students"] = [{"name": s[0], "dob": str(s[1]), "course": s[2]} for s in matching_students]
            return facts
        elif rel == "before":
            count = db.query(func.count(Student.student_id)).filter(extract("year", Student.dob) < year).scalar() or 0
            matching_students = db.query(Student.name, Student.dob, Student.course).filter(extract("year", Student.dob) < year).all()
            facts["matched_intent"] = "students_by_dob"
            facts["condition"] = f"born before {year}"
            facts["count"] = count
            facts["students"] = [{"name": s[0], "dob": str(s[1]), "course": s[2]} for s in matching_students]
            return facts

    # Check course query:
    courses = db.query(Student.course).filter(Student.course.isnot(None)).distinct().all()
    course_names = [c[0] for c in courses if c[0]]

    matched_course = None
    for c_name in course_names:
        if c_name.lower() in q:
            matched_course = c_name
            break

    if matched_course:
        students = db.query(Student.name, Student.enrollment_date).filter(Student.course == matched_course).all()
        facts["matched_intent"] = "students_by_course"
        facts["course"] = matched_course
        facts["count"] = len(students)
        facts["students"] = [{"name": s[0], "enrollment_date": str(s[1]) if s[1] else "N/A"} for s in students]
        return facts

    # General course breakdown
    course_counts = (
        db.query(Student.course, func.count(Student.student_id))
        .group_by(Student.course)
        .all()
    )
    facts["courses"] = {c or "Unassigned": cnt for c, cnt in course_counts}
    return facts

def generate_fallback_answer(facts: Dict[str, Any], question: str) -> str:
    """Generates an accurate, deterministic response using verified facts."""
    intent = facts.get("matched_intent")
    total = facts.get("total_students", 0)

    if intent == "empty_database":
        return "There are currently no students registered in the system."

    if intent == "students_by_dob":
        cond = facts.get("condition")
        cnt = facts.get("count", 0)
        names = [s["name"] for s in facts.get("students", [])[:5]]
        preview = f" (including {', '.join(names)})" if names else ""
        return f"There are {cnt} student(s) {cond}{preview}."

    if intent == "students_by_course":
        course = facts.get("course")
        cnt = facts.get("count", 0)
        names = [s["name"] for s in facts.get("students", [])[:5]]
        preview = f" ({', '.join(names)})" if names else ""
        return f"There are {cnt} student(s) enrolled in {course}{preview}."

    courses_dict = facts.get("courses", {})
    courses_str = ", ".join([f"{k}: {v}" for k, v in courses_dict.items()])
    return f"There are {total} total registered students across the institution. Course enrollment breakdown: {courses_str}."

async def query_student_ai(db: Session, question: str) -> Dict[str, Any]:
    """Processes natural language questions safely with controlled backend facts."""
    facts = parse_and_retrieve_facts(db, question)
    fallback_text = generate_fallback_answer(facts, question)

    system_prompt = (
        "You are an academic records assistant for EWB Edu Tech. "
        "Answer the user's question accurately using ONLY the verified facts provided below. "
        "Keep answers concise, direct, professional, and friendly. Do not invent student data.\n"
        f"Verified Database Facts: {facts}"
    )

    # Try calling Ollama safely if running
    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": f"System: {system_prompt}\nUser Question: {question}\nAnswer:",
                    "stream": False
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("response", "").strip()
                if answer:
                    return {
                        "question": question,
                        "answer": answer,
                        "source": f"ollama ({settings.OLLAMA_MODEL})",
                        "data_summary": facts
                    }
    except Exception:
        # Graceful fallback: Ollama not running, timed out, or model not downloaded
        pass

    return {
        "question": question,
        "answer": fallback_text,
        "source": "verified_rule_engine",
        "data_summary": facts
    }
