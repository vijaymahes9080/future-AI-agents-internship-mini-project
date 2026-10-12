# EWB Student Record Management System

A complete, production-grade, professional Student Record Management System built for the **EWB Edu Tech Pvt. Ltd.** internship assignment.

Engineered with **Python 3.11+**, **FastAPI**, **SQLite**, **SQLAlchemy ORM**, **Pydantic v2**, and a modern academic administration dashboard built with clean Vanilla HTML5, CSS3, and JavaScript.

---

## 1. Project Objective

The objective of this project is to provide higher education institutions and academic administration teams with a centralized, reliable, and secure platform to manage the complete lifecycle of student records. The system guarantees atomic CRUD operations, strict data validation, deterministic search and filtering, real-time analytics, and optional local AI-powered query assistance via Ollama.

---

## 2. Features

- **Full RESTful CRUD API:**
  - `POST /students`: Register new students with contact validation (HTTP 201).
  - `GET /students`: Query records with debounced name search, course filtering, and pagination (`skip`/`limit`).
  - `GET /students/{id}`: Detailed student profile lookup with standard 404 responses.
  - `PUT /students/{id}`: Complete record replacement preserving primary key integrity.
  - `PATCH /students/{id}`: Granular updates preserving omitted fields and verifying resulting integrity.
  - `DELETE /students/{id}`: Idempotent student record deletion with HTTP 204 (repeat deletion returns 404).
- **Academic Administration Dashboard:**
  - Executive KPI summary: Total registered students, active courses, and persistence status.
  - Live course enrollment distribution with proportional visual indicators.
  - Real-time student directory table with instant name search and course dropdown filters.
  - Student creation and editing modal dialogs with dual client-side & server-side error validation.
  - Detailed student profile card view.
  - Safe student deletion confirmation flow.
- **Local AI Academic Assistant (Optional Enhancement):**
  - Natural language querying powered by controlled backend data aggregation.
  - Safe Python analytics engine (zero arbitrary SQL/code execution).
  - Seamless, graceful fallback if Ollama is offline or unavailable.
- **Automated Quality Assurance:**
  - Comprehensive pytest suite covering 20 isolated test scenarios across Create, Read, Update, Delete, Persistence, and AI fallback.

---

## 3. Technology Stack

- **Backend:** Python 3.11+, FastAPI 0.110+, Starlette, Uvicorn
- **Database & ORM:** SQLite 3, SQLAlchemy 2.0+
- **Validation:** Pydantic v2, Email-Validator
- **Frontend:** Vanilla HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid, Inter typography), Vanilla JavaScript (ES6+ Fetch API)
- **Testing:** Pytest, HTTPX, FastAPI TestClient
- **Optional Local AI:** Ollama (`llama3.2:1b`)

---

## 4. Application Architecture

```
                      +---------------------------------------+
                      |       Web Browser / API Client        |
                      +---------------------------------------+
                                  |                 |
                    Static Assets |                 | REST API (/students, /stats, /ai)
                                  v                 v
                      +---------------------------------------+
                      |         FastAPI Application           |
                      |   (Dependency Injection & Routers)   |
                      +---------------------------------------+
                           |              |             |
                           v              v             v
                    +------------+  +-----------+  +-------------------+
                    | Pydantic   |  | SQLAlchemy|  | AI Query Service  |
                    | Schemas &  |  | Models &  |  | (Safe Aggregation |
                    | Validation |  | CRUD Ops  |  |  + Ollama Client) |
                    +------------+  +-----------+  +-------------------+
                                          |                 |
                                          v                 v
                                   +-------------+   +---------------+
                                   |  SQLite DB  |   | Ollama Server |
                                   | (students.db|   | (Optional)    |
                                   +-------------+   +---------------+
```

---

## 5. Project Structure

```
.
├── app/
│   ├── __init__.py           # Package declaration & version
│   ├── config.py             # Application settings & environment variables
│   ├── database.py           # SQLite connection, engine & session management
│   ├── models.py             # SQLAlchemy Student ORM entity
│   ├── schemas.py            # Pydantic v2 schemas and validation logic
│   ├── crud.py               # Database CRUD operations and sample data seeder
│   ├── main.py               # FastAPI application factory, lifespan, routes
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py       # REST API endpoints for student records
│   │   ├── stats.py          # Dashboard analytics & course list endpoints
│   │   └── ai.py             # AI Assistant query endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py     # Intent parsing, verified facts & Ollama client
│   └── static/
│       ├── index.html        # Administration dashboard web interface
│       ├── css/
│       │   └── style.css     # Clean academic SaaS stylesheet
│       └── js/
│           └── app.js        # Dashboard state, DOM rendering & API calls
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures and isolated SQLite setup
│   └── test_students.py      # 20 automated tests for API, persistence, AI
├── .gitignore                # Git exclusions (venv, db, caches, logs)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 6. Installation & Windows Setup

### Step 1: Clone the repository or navigate to the project directory
```powershell
cd "d:\current project\future AI agent\vj"
```

### Step 2: Create a virtual environment
```powershell
python -m venv .venv
```

### Step 3: Activate the virtual environment in PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If script execution is disabled on your system, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 4: Install dependencies
```powershell
python -m pip install -r requirements.txt
```

---

## 7. Database Initialization and Persistence

The database engine is configured in [app/database.py](file:///d:/current%20project/future%20AI%20agent/vj/app/database.py) using SQLite:
- By default, it connects to a local, project-relative database file `students.db`.
- Database tables are automatically initialized during FastAPI application startup via `init_db()`.
- If the database is freshly created, realistic fictional student records are automatically seeded so that the dashboard displays data immediately.
- SQLite writes all changes directly to the persistent disk file, guaranteeing records survive server restarts.

---

## 8. Starting the Application

Launch the server using Uvicorn:

```powershell
python -m uvicorn app.main:app --reload
```

Once running, access the services:
- **Interactive Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 9. API Endpoints

| HTTP Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/students` | Register a new student | `201 Created` |
| `GET` | `/students` | List, search, filter, and paginate students | `200 OK` |
| `GET` | `/students/{id}` | Retrieve a student record by ID | `200 OK` / `404 Not Found` |
| `PUT` | `/students/{id}` | Replace editable student details | `200 OK` / `404 Not Found` |
| `PATCH` | `/students/{id}` | Update specific student fields | `200 OK` / `404 Not Found` |
| `DELETE` | `/students/{id}` | Permanently delete a student record | `204 No Content` / `404` |
| `GET` | `/stats` | Aggregated dashboard metrics & course breakdown | `200 OK` |
| `GET` | `/stats/courses` | List of all distinct courses | `200 OK` |
| `POST` | `/ai/ask` | Natural language questions about student data | `200 OK` |
| `GET` | `/health` | Service health status | `200 OK` |

---

## 10. Example JSON Payloads

### Create Student (`POST /students`)
```json
{
  "name": "Ananya Sharma",
  "dob": "2003-05-18",
  "email": "ananya.sharma@ewbedutech.org",
  "phone": "+91 98765 12345",
  "course": "Artificial Intelligence",
  "address": "45 Knowledge Park, Bangalore",
  "enrollment_date": "2024-08-01"
}
```

### Partial Update (`PATCH /students/1`)
```json
{
  "course": "Data Science",
  "phone": "+91 98765 99999"
}
```

### AI Query (`POST /ai/ask`)
```json
{
  "question": "How many students are enrolled in Artificial Intelligence?"
}
```

---

## 11. Automated Testing

The project includes 20 comprehensive unit and integration tests run against an isolated SQLite test database.

Execute the test suite:
```powershell
.\.venv\Scripts\pytest.exe -v
```

### Test Coverage Highlights:
- **Create:** Valid student registration, rejection of empty names, missing dates of birth, invalid emails, and rejection when both contact methods are absent.
- **Read:** Empty database handling, ID retrieval, 404 on missing records, case-insensitive partial search, course filter, deterministic pagination with disjoint sets.
- **Update:** Complete PUT updates, partial PATCH updates preserving untouched fields, rejection of invalid contact updates, 404 checks.
- **Delete:** Successful deletion (204), subsequent retrieval returning 404, repeated deletion returning 404.
- **Persistence:** Verifies student records survive session closes and database reconnection.
- **AI Fallback:** Safe facts extraction and response generation even when local LLM is offline.

---

## 12. Optional Local AI Setup (Ollama)

To enable local LLM-powered natural language answers:
1. Install [Ollama](https://ollama.com/).
2. Pull the default lightweight model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Start Ollama:
   ```bash
   ollama serve
   ```
4. If Ollama is running, the backend forwards the verified facts context to Ollama.
5. If Ollama is not installed or unreachable, the system automatically falls back to its internal verified rules engine without interrupting any core application workflows.

---

## 13. Security and Privacy

- **Safe Aggregations:** AI assistant never translates user prompts directly into SQL. All calculations are executed via controlled Python logic.
- **Data Protection:** Contact details are strictly omitted from prompts sent to AI models.
- **SQL Injection Prevention:** All database operations utilize SQLAlchemy ORM parameterized queries.
- **Git Exclusions:** The local database files (`*.db`), virtual environments (`.venv`), and temporary caches are explicitly listed in `.gitignore`.

---

## 14. Git Submission Commands

To submit this project to your GitHub repository:

```powershell
git init
git add .
git commit -m "feat: complete EWB student record management system with FastAPI, SQLite, Dashboard, and Pytest"
git remote add origin https://github.com/vijaymahes9080/future-AI-agents-internship-mini-project.git
git branch -M main
git push -u origin main
```
