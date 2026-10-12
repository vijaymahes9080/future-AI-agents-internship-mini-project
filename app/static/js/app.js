/**
 * EWB Student Record Management System - Frontend Application
 */

const API_BASE = "";

// State
let currentTab = "dashboard";
let currentPage = 1;
const pageSize = 8;
let totalRecords = 0;
let searchQuery = "";
let selectedCourse = "";
let searchDebounceTimer = null;
let currentProfileStudent = null;
let pendingDeleteId = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  checkBackendHealth();
  await loadCoursesList();
  await loadDashboardStats();
  await loadStudentsDirectory();

  // Setup search debouncing
  const searchInput = document.getElementById("filter-search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        searchQuery = e.target.value.trim();
        currentPage = 1;
        loadStudentsDirectory();
      }, 350);
    });
  }

  // Setup course filter
  const courseSelect = document.getElementById("filter-course");
  if (courseSelect) {
    courseSelect.addEventListener("change", (e) => {
      selectedCourse = e.target.value;
      currentPage = 1;
      loadStudentsDirectory();
    });
  }
}

// Backend Health Status
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      document.getElementById("system-status").style.display = "inline-flex";
      document.getElementById("status-text").textContent = "FastAPI & SQLite Active";
    }
  } catch (err) {
    const statusBadge = document.getElementById("system-status");
    statusBadge.className = "system-status-badge alert-danger";
    document.getElementById("status-text").textContent = "Backend Disconnected";
  }
}

// Navigation Tabs
function switchTab(tabId) {
  currentTab = tabId;

  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(el => el.classList.remove("active"));

  const navBtn = document.getElementById(`nav-${tabId}`);
  if (navBtn) navBtn.classList.add("active");

  const pane = document.getElementById(`tab-${tabId}`);
  if (pane) pane.classList.add("active");

  const heading = document.getElementById("page-heading");
  if (tabId === "dashboard") {
    heading.textContent = "Dashboard Overview";
    loadDashboardStats();
  } else if (tabId === "students") {
    heading.textContent = "Student Directory";
    loadStudentsDirectory();
  } else if (tabId === "ai") {
    heading.textContent = "Academic AI Assistant";
  }
}

function refreshCurrentView() {
  if (currentTab === "dashboard") {
    loadDashboardStats();
  } else if (currentTab === "students") {
    loadStudentsDirectory();
  }
  showToast("Data refreshed successfully", "success");
}

// Load Distinct Courses for Dropdowns
async function loadCoursesList() {
  try {
    const res = await fetch(`${API_BASE}/stats/courses`);
    if (res.ok) {
      const courses = await res.json();
      const filterSelect = document.getElementById("filter-course");
      if (filterSelect) {
        filterSelect.innerHTML = '<option value="">All Courses</option>';
        courses.forEach(c => {
          const opt = document.createElement("option");
          opt.value = c;
          opt.textContent = c;
          filterSelect.appendChild(opt);
        });
      }
    }
  } catch (err) {
    console.error("Failed to load courses:", err);
  }
}

// Load Dashboard Statistics
async function loadDashboardStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error("Failed to fetch dashboard statistics");

    const data = await res.json();

    // KPIs
    document.getElementById("kpi-total-students").textContent = data.total_students;
    document.getElementById("kpi-total-courses").textContent = data.total_courses;

    // Course Distribution Bars
    const distContainer = document.getElementById("course-distribution-list");
    distContainer.innerHTML = "";

    if (!data.course_distribution || data.course_distribution.length === 0) {
      distContainer.innerHTML = '<div class="text-muted text-center py-4">No course data available.</div>';
    } else {
      const maxCount = Math.max(...data.course_distribution.map(d => d.count), 1);
      data.course_distribution.forEach(item => {
        const percent = Math.round((item.count / maxCount) * 100);
        const div = document.createElement("div");
        div.className = "distribution-item";
        div.innerHTML = `
          <div class="distribution-meta">
            <span class="distribution-title">${escapeHtml(item.course)}</span>
            <span class="distribution-count">${item.count} student${item.count === 1 ? '' : 's'}</span>
          </div>
          <div class="progress-track">
            <div class="progress-bar" style="width: ${percent}%;"></div>
          </div>
        `;
        distContainer.appendChild(div);
      });
    }

    // Recently Enrolled Table
    const recentTbody = document.getElementById("recent-students-tbody");
    recentTbody.innerHTML = "";

    if (!data.recent_enrollments || data.recent_enrollments.length === 0) {
      recentTbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No students enrolled yet.</td></tr>';
    } else {
      data.recent_enrollments.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>#${s.student_id}</strong></td>
          <td><strong>${escapeHtml(s.name)}</strong></td>
          <td><span class="badge badge-course">${escapeHtml(s.course || 'Unassigned')}</span></td>
          <td>${formatDate(s.enrollment_date)}</td>
        `;
        recentTbody.appendChild(tr);
      });
    }

  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

// Load Students Directory with Pagination and Search
async function loadStudentsDirectory() {
  const tbody = document.getElementById("students-tbody");
  tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-muted">Loading students...</td></tr>';

  const skip = (currentPage - 1) * pageSize;
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: pageSize.toString()
  });

  if (searchQuery) params.append("search", searchQuery);
  if (selectedCourse) params.append("course", selectedCourse);

  try {
    const res = await fetch(`${API_BASE}/students?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to load students");

    const data = await res.json();
    totalRecords = data.total;

    // Update Counts Bar
    const countText = document.getElementById("results-count-text");
    if (totalRecords === 0) {
      countText.textContent = "No student records found.";
    } else {
      const from = skip + 1;
      const to = Math.min(skip + pageSize, totalRecords);
      countText.textContent = `Showing ${from}–${to} of ${totalRecords} student${totalRecords === 1 ? '' : 's'}`;
    }

    // Render Table Rows
    tbody.innerHTML = "";
    if (data.items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center py-8">
            <div style="color: var(--text-muted); font-size: 0.95rem;">
              No students match your filter criteria.
            </div>
            <button class="btn btn-secondary btn-sm" style="margin-top: 10px;" onclick="resetFilters()">Reset Filters</button>
          </td>
        </tr>
      `;
    } else {
      data.items.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>#${s.student_id}</strong></td>
          <td>
            <div class="student-name-cell">
              <span class="student-name">${escapeHtml(s.name)}</span>
              <span class="student-meta-sub">${s.address ? escapeHtml(s.address.slice(0, 30)) + (s.address.length > 30 ? '...' : '') : 'No address'}</span>
            </div>
          </td>
          <td>
            <div class="contact-cell">
              <span class="contact-email">${s.email ? escapeHtml(s.email) : '—'}</span>
              <span class="contact-phone">${s.phone ? escapeHtml(s.phone) : '—'}</span>
            </div>
          </td>
          <td><span class="badge badge-course">${escapeHtml(s.course || 'Unassigned')}</span></td>
          <td>${formatDate(s.dob)}</td>
          <td>${formatDate(s.enrollment_date)}</td>
          <td>
            <div class="action-buttons">
              <button class="action-btn" title="View Profile" onclick="viewProfile(${s.student_id})">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
              <button class="action-btn" title="Edit Student" onclick="editStudent(${s.student_id})">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
              </button>
              <button class="action-btn delete-btn" title="Delete Student" onclick="confirmDeleteStudent(${s.student_id}, '${escapeQuote(s.name)}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    // Update Pagination Controls
    const totalPages = Math.ceil(totalRecords / pageSize) || 1;
    document.getElementById("pagination-info").textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById("page-indicator").textContent = currentPage;
    document.getElementById("btn-prev-page").disabled = (currentPage <= 1);
    document.getElementById("btn-next-page").disabled = (currentPage >= totalPages);

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 alert-danger">Error loading records: ${err.message}</td></tr>`;
  }
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    loadStudentsDirectory();
  }
}

function nextPage() {
  const totalPages = Math.ceil(totalRecords / pageSize);
  if (currentPage < totalPages) {
    currentPage++;
    loadStudentsDirectory();
  }
}

function resetFilters() {
  searchQuery = "";
  selectedCourse = "";
  const sInput = document.getElementById("filter-search");
  if (sInput) sInput.value = "";
  const cSelect = document.getElementById("filter-course");
  if (cSelect) cSelect.value = "";
  currentPage = 1;
  loadStudentsDirectory();
}

// Student Form Modal (Create & Edit)
function openStudentModal() {
  document.getElementById("student-id-field").value = "";
  document.getElementById("modal-title").textContent = "Register New Student";
  document.getElementById("save-btn-text").textContent = "Save Student Record";
  document.getElementById("student-form").reset();
  hideFormError();
  document.getElementById("student-modal").classList.add("open");
}

function closeStudentModal() {
  document.getElementById("student-modal").classList.remove("open");
  hideFormError();
}

async function editStudent(studentId) {
  hideFormError();
  try {
    const res = await fetch(`${API_BASE}/students/${studentId}`);
    if (!res.ok) throw new Error("Could not retrieve student details");

    const s = await res.json();
    document.getElementById("student-id-field").value = s.student_id;
    document.getElementById("modal-title").textContent = `Edit Student (ID: #${s.student_id})`;
    document.getElementById("save-btn-text").textContent = "Update Student";

    document.getElementById("form-name").value = s.name || "";
    document.getElementById("form-dob").value = s.dob || "";
    document.getElementById("form-enrollment-date").value = s.enrollment_date || "";
    document.getElementById("form-email").value = s.email || "";
    document.getElementById("form-phone").value = s.phone || "";
    document.getElementById("form-course").value = s.course || "";
    document.getElementById("form-address").value = s.address || "";

    document.getElementById("student-modal").classList.add("open");
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function handleStudentFormSubmit(e) {
  e.preventDefault();
  hideFormError();

  const id = document.getElementById("student-id-field").value;
  const name = document.getElementById("form-name").value.trim();
  const dob = document.getElementById("form-dob").value;
  const enrollment_date = document.getElementById("form-enrollment-date").value || null;
  const email = document.getElementById("form-email").value.trim() || null;
  const phone = document.getElementById("form-phone").value.trim() || null;
  const course = document.getElementById("form-course").value.trim() || null;
  const address = document.getElementById("form-address").value.trim() || null;

  // Validation
  if (!name) {
    showFormError("Student name is required.");
    return;
  }
  if (!dob) {
    showFormError("Date of birth is required.");
    return;
  }
  if (!email && !phone) {
    showFormError("Contact Policy: At least one contact method (Email or Phone) must be provided.");
    return;
  }

  const payload = {
    name,
    dob,
    enrollment_date,
    email,
    phone,
    course,
    address
  };

  const saveBtn = document.getElementById("btn-save-student");
  const spinner = document.getElementById("save-spinner");
  const btnText = document.getElementById("save-btn-text");

  saveBtn.disabled = true;
  spinner.style.display = "inline-block";

  try {
    const isEdit = Boolean(id);
    const url = isEdit ? `${API_BASE}/students/${id}` : `${API_BASE}/students`;
    const method = isEdit ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          showFormError(data.detail.map(d => `${d.loc.slice(-1)}: ${d.msg}`).join("<br>"));
        } else {
          showFormError(data.detail);
        }
      } else {
        showFormError("Failed to save student record.");
      }
      return;
    }

    closeStudentModal();
    showToast(isEdit ? "Student details updated successfully!" : "Student registered successfully!", "success");
    await loadCoursesList();
    await loadDashboardStats();
    await loadStudentsDirectory();

  } catch (err) {
    showFormError("Network error: Unable to contact server.");
  } finally {
    saveBtn.disabled = false;
    spinner.style.display = "none";
  }
}

function showFormError(msg) {
  const banner = document.getElementById("form-error-banner");
  banner.innerHTML = msg;
  banner.style.display = "block";
}

function hideFormError() {
  const banner = document.getElementById("form-error-banner");
  banner.style.display = "none";
}

// Student Profile Modal
async function viewProfile(studentId) {
  try {
    const res = await fetch(`${API_BASE}/students/${studentId}`);
    if (!res.ok) throw new Error("Could not retrieve student profile");

    const s = await res.json();
    currentProfileStudent = s;

    document.getElementById("prof-name").textContent = s.name;
    document.getElementById("prof-course").textContent = s.course || "No Course Assigned";
    document.getElementById("prof-avatar").textContent = getInitials(s.name);

    document.getElementById("prof-id").textContent = `#${s.student_id}`;
    document.getElementById("prof-dob").textContent = formatDate(s.dob);
    document.getElementById("prof-email").textContent = s.email || "—";
    document.getElementById("prof-phone").textContent = s.phone || "—";
    document.getElementById("prof-enrollment").textContent = formatDate(s.enrollment_date);
    document.getElementById("prof-created").textContent = s.created_at ? new Date(s.created_at).toLocaleDateString() : "—";
    document.getElementById("prof-address").textContent = s.address || "—";

    document.getElementById("profile-modal").classList.add("open");
  } catch (err) {
    showToast(err.message, "error");
  }
}

function closeProfileModal() {
  document.getElementById("profile-modal").classList.remove("open");
}

function editFromProfile() {
  if (currentProfileStudent) {
    closeProfileModal();
    editStudent(currentProfileStudent.student_id);
  }
}

// Student Deletion Modal
function confirmDeleteStudent(studentId, studentName) {
  pendingDeleteId = studentId;
  document.getElementById("del-student-id").textContent = studentId;
  document.getElementById("del-student-name").textContent = studentName;
  document.getElementById("delete-modal").classList.add("open");
}

function closeDeleteModal() {
  document.getElementById("delete-modal").classList.remove("open");
  pendingDeleteId = null;
}

async function executeDeleteStudent() {
  if (!pendingDeleteId) return;

  const btn = document.getElementById("btn-confirm-delete");
  const spinner = document.getElementById("del-spinner");
  btn.disabled = true;
  spinner.style.display = "inline-block";

  try {
    const res = await fetch(`${API_BASE}/students/${pendingDeleteId}`, {
      method: "DELETE"
    });

    if (res.status === 204) {
      closeDeleteModal();
      showToast("Student record deleted successfully.", "success");
      await loadCoursesList();
      await loadDashboardStats();
      await loadStudentsDirectory();
    } else {
      const data = await res.json();
      showToast(data.detail || "Deletion failed.", "error");
    }
  } catch (err) {
    showToast("Network error during deletion.", "error");
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
  }
}

// AI Assistant
function askPreset(question) {
  document.getElementById("ai-question-input").value = question;
  handleAISubmit(new Event("submit"));
}

async function handleAISubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("ai-question-input");
  const question = input.value.trim();
  if (!question) return;

  const btn = document.getElementById("btn-ask-ai");
  const spinner = document.getElementById("ai-spinner");
  const btnText = document.getElementById("ai-btn-text");
  const responseBox = document.getElementById("ai-response-box");
  const responseText = document.getElementById("ai-response-text");
  const sourceBadge = document.getElementById("ai-source-badge");
  const factsPreview = document.getElementById("ai-facts-preview");
  const factsJson = document.getElementById("ai-facts-json");

  btn.disabled = true;
  spinner.style.display = "inline-block";
  btnText.textContent = "Analyzing...";

  try {
    const res = await fetch(`${API_BASE}/ai/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "AI query failed");

    responseBox.style.display = "block";
    responseText.textContent = data.answer;
    sourceBadge.textContent = `Source: ${data.source}`;

    if (data.data_summary) {
      factsPreview.style.display = "block";
      factsJson.textContent = JSON.stringify(data.data_summary, null, 2);
    } else {
      factsPreview.style.display = "none";
    }

  } catch (err) {
    responseBox.style.display = "block";
    responseText.textContent = `Could not process query: ${err.message}`;
    sourceBadge.textContent = "Error";
    factsPreview.style.display = "none";
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
    btnText.textContent = "Ask Assistant";
  }
}

// Utility Helpers
function formatDate(dateStr) {
  if (!dateStr) return "—";
  try {
    const [y, m, d] = dateStr.split("-");
    const date = new Date(parseInt(y), parseInt(m) - 1, parseInt(d));
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return dateStr;
  }
}

function getInitials(name) {
  if (!name) return "ST";
  const parts = name.trim().split(" ");
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeQuote(str) {
  if (!str) return "";
  return String(str).replace(/'/g, "\\'");
}

function showToast(msg, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
