import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Student
from app.database import Base

# --- CREATE TESTS ---

def test_create_student_success(client):
    payload = {
        "name": "Arjun Rao",
        "dob": "2003-04-12",
        "email": "arjun.rao@example.com",
        "phone": "+91 91234 56789",
        "course": "Artificial Intelligence",
        "address": "12 Silicon Avenue, Bangalore",
        "enrollment_date": "2024-07-20"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Arjun Rao"
    assert data["dob"] == "2003-04-12"
    assert data["email"] == "arjun.rao@example.com"
    assert "student_id" in data
    assert data["student_id"] > 0

def test_create_student_missing_name(client):
    payload = {
        "name": "   ",
        "dob": "2003-04-12",
        "email": "test@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422

def test_create_student_missing_dob(client):
    payload = {
        "name": "Valid Name",
        "email": "test@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422

def test_create_student_invalid_email(client):
    payload = {
        "name": "Valid Name",
        "dob": "2002-01-01",
        "email": "invalid-email-address",
        "phone": "+91 99999 88888"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422

def test_create_student_invalid_date(client):
    payload = {
        "name": "Valid Name",
        "dob": "not-a-date",
        "email": "test@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422

def test_create_student_missing_both_contact_methods(client):
    payload = {
        "name": "No Contact Student",
        "dob": "2002-05-15",
        "course": "Data Science"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "contact method" in response.text.lower()

# --- READ TESTS ---

def test_get_all_students_empty(client):
    response = client.get("/students")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []

def test_get_student_by_id(client):
    # Insert student
    res_create = client.post("/students", json={
        "name": "Bhavna Patel",
        "dob": "2002-08-19",
        "email": "bhavna@example.com"
    })
    student_id = res_create.json()["student_id"]

    # Fetch
    res_get = client.get(f"/students/{student_id}")
    assert res_get.status_code == 200
    assert res_get.json()["student_id"] == student_id
    assert res_get.json()["name"] == "Bhavna Patel"

def test_get_student_not_found(client):
    response = client.get("/students/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_search_by_name(client):
    client.post("/students", json={"name": "Alice Smith", "dob": "2001-01-01", "email": "alice@ex.com"})
    client.post("/students", json={"name": "Bob Jones", "dob": "2001-02-02", "email": "bob@ex.com"})
    client.post("/students", json={"name": "Alice Wonderland", "dob": "2001-03-03", "email": "alice2@ex.com"})

    response = client.get("/students?search=alice")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert "alice" in item["name"].lower()

def test_filter_by_course(client):
    client.post("/students", json={"name": "CS Student", "dob": "2001-01-01", "email": "cs@ex.com", "course": "Computer Science"})
    client.post("/students", json={"name": "AI Student", "dob": "2001-02-02", "email": "ai@ex.com", "course": "Artificial Intelligence"})

    response = client.get("/students?course=Computer Science")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["course"] == "Computer Science"

def test_pagination(client):
    for i in range(15):
        client.post("/students", json={"name": f"Student {i}", "dob": "2002-01-01", "email": f"s{i}@ex.com"})

    res_page1 = client.get("/students?skip=0&limit=5")
    assert res_page1.status_code == 200
    d1 = res_page1.json()
    assert d1["total"] == 15
    assert len(d1["items"]) == 5

    res_page2 = client.get("/students?skip=5&limit=5")
    assert res_page2.status_code == 200
    d2 = res_page2.json()
    assert len(d2["items"]) == 5
    # Assert deterministic distinct elements
    ids1 = [item["student_id"] for item in d1["items"]]
    ids2 = [item["student_id"] for item in d2["items"]]
    assert set(ids1).isdisjoint(set(ids2))

# --- UPDATE TESTS ---

def test_full_put_update(client):
    res_create = client.post("/students", json={
        "name": "Original Name",
        "dob": "2001-05-10",
        "email": "orig@ex.com",
        "course": "Physics"
    })
    s_id = res_create.json()["student_id"]

    put_payload = {
        "name": "Updated Full Name",
        "dob": "2001-05-10",
        "email": "updated@ex.com",
        "phone": "+91 98765 00000",
        "course": "Computer Science",
        "address": "New Address",
        "enrollment_date": "2024-09-01"
    }
    res_put = client.put(f"/students/{s_id}", json=put_payload)
    assert res_put.status_code == 200
    updated = res_put.json()
    assert updated["student_id"] == s_id
    assert updated["name"] == "Updated Full Name"
    assert updated["course"] == "Computer Science"
    assert updated["phone"] == "+91 98765 00000"

def test_partial_patch_update(client):
    res_create = client.post("/students", json={
        "name": "Patch Target",
        "dob": "2002-02-02",
        "email": "patch@ex.com",
        "course": "Mathematics"
    })
    s_id = res_create.json()["student_id"]

    # Patch only course
    res_patch = client.patch(f"/students/{s_id}", json={"course": "Data Science"})
    assert res_patch.status_code == 200
    patched = res_patch.json()
    assert patched["course"] == "Data Science"
    assert patched["name"] == "Patch Target"  # preserved
    assert patched["email"] == "patch@ex.com"  # preserved

def test_patch_reject_removal_of_all_contacts(client):
    res_create = client.post("/students", json={
        "name": "Contact Removal Test",
        "dob": "2002-02-02",
        "email": "onlycontact@ex.com"
    })
    s_id = res_create.json()["student_id"]

    # Try removing the only contact method
    res_patch = client.patch(f"/students/{s_id}", json={"email": "   "})
    assert res_patch.status_code == 422

def test_update_student_not_found(client):
    res = client.put("/students/8888", json={
        "name": "Ghost",
        "dob": "2000-01-01",
        "email": "ghost@ex.com"
    })
    assert res.status_code == 404

# --- DELETE TESTS ---

def test_delete_student_success_and_repeat_404(client):
    res_create = client.post("/students", json={
        "name": "To Be Deleted",
        "dob": "2002-03-03",
        "email": "delete@ex.com"
    })
    s_id = res_create.json()["student_id"]

    # First delete -> 204
    res_del = client.delete(f"/students/{s_id}")
    assert res_del.status_code == 204

    # Subsequent GET -> 404
    res_get = client.get(f"/students/{s_id}")
    assert res_get.status_code == 404

    # Repeated DELETE -> 404
    res_del_repeat = client.delete(f"/students/{s_id}")
    assert res_del_repeat.status_code == 404

# --- PERSISTENCE TESTS ---

def test_persistence_across_reconnect(test_db_file):
    """Verify that records survive database reconnection and new session creation."""
    engine = create_engine(f"sqlite:///{test_db_file}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    # Insert record in session 1
    session1 = Session()
    new_student = Student(
        name="Persistent Student",
        dob=date(2001, 1, 1),
        email="persist@example.com",
        course="Cybersecurity"
    )
    session1.add(new_student)
    session1.commit()
    s_id = new_student.student_id
    session1.close()

    # Reconnect in fresh session 2
    session2 = Session()
    reloaded = session2.query(Student).filter(Student.student_id == s_id).first()
    assert reloaded is not None
    assert reloaded.name == "Persistent Student"
    assert reloaded.course == "Cybersecurity"
    session2.close()

# --- INTEGRATION & DASHBOARD STATS ---

def test_dashboard_stats_endpoint(client):
    client.post("/students", json={"name": "Stats 1", "dob": "2001-01-01", "email": "s1@ex.com", "course": "AI"})
    client.post("/students", json={"name": "Stats 2", "dob": "2001-01-01", "email": "s2@ex.com", "course": "AI"})
    client.post("/students", json={"name": "Stats 3", "dob": "2001-01-01", "email": "s3@ex.com", "course": "Robotics"})

    res = client.get("/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 3
    assert data["total_courses"] == 2
    assert len(data["recent_enrollments"]) == 3
    courses_map = {item["course"]: item["count"] for item in data["course_distribution"]}
    assert courses_map["AI"] == 2
    assert courses_map["Robotics"] == 1

def test_ai_assistant_query_without_ollama(client):
    """Verify that the AI assistant answers safely using verified facts even if Ollama is offline."""
    client.post("/students", json={"name": "AI Query Student", "dob": "2001-01-01", "email": "aiq@ex.com", "course": "AI"})

    res = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "source" in data
    assert "data_summary" in data
    assert data["data_summary"]["total_students"] >= 1
