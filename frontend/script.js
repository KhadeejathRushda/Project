/* ================= BASE URLS ================= */
const AUTH_URL = "http://127.0.0.1:8000/api/accounts/"; 
const BASE_URL = "http://127.0.0.1:8000/api/reports/"; 
const MEDIA_BASE = "http://127.0.0.1:8000"; 

/* ================= AUTH HELPERS ================= */
function checkAuth(res) {
    if (res.status === 401) {
        alert("Session expired. Please login again.");
        logout();
        throw new Error("Unauthorized");
    }
    return res.json();
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

/* ================= AUTHENTICATION ================= */
function login() {
    const username = document.getElementById("username")?.value;
    const password = document.getElementById("password")?.value;

    if (!username || !password) return alert("Enter username & password");

    fetch(AUTH_URL + "login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.access) {
            localStorage.setItem("token", data.access);
            localStorage.setItem("role", data.role);
            localStorage.setItem("username", data.username);
            localStorage.setItem("user_id", data.user_id);
            window.location.href = data.role === "patient" ? "reports.html" : "dashboard.html";
        } else {
            alert(data.error || "Login Failed");
        }
    })
    .catch(() => alert("Server error: Is the backend running?"));
}

function handleRoleChange() {
    const role = document.getElementById('role').value;
    const certDiv = document.getElementById('certificateDiv');
    const docDiv = document.getElementById('doctorDiv');

    if (certDiv) certDiv.style.display = "none";
    if (docDiv) docDiv.style.display = "none";

    if (role === 'doctor' && certDiv) {
        certDiv.style.display = "block";
    } else if (role === 'patient' && docDiv) {
        docDiv.style.display = "block";
        loadDoctors();
    }
}

function registerUser() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    
    if (!username || !password || !role) return alert("Fill all required fields");

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    formData.append("role", role);
    formData.append("name", name);
    formData.append("email", email);

    if (role === "doctor") {
        const cert = document.getElementById("certificate")?.files[0];
        if (!cert) return alert("Doctor must upload a certificate");
        formData.append("certificate", cert);
    } else if (role === "patient") {
        const docId = document.getElementById("doctor")?.value;
        if (!docId) return alert("Patient must select a doctor");
        formData.append("assigned_doctor", docId);
    }

    fetch(AUTH_URL + "register/", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.message || data.username) {
            alert("Registered successfully! If you are a doctor, wait for admin approval.");
            window.location.href = "login.html";
        } else {
            alert("Registration failed: " + JSON.stringify(data));
        }
    })
    .catch(() => alert("Server error during registration"));
}

/* ================= DATA LOADING ================= */
function loadDoctors() {
    const select = document.getElementById("doctor");
    if (!select) return;

    fetch(AUTH_URL + "doctors/") 
    .then(res => res.json())
    .then(data => {
        select.innerHTML = `<option value="">Select Doctor</option>`;
        data.forEach(doc => {
            const opt = document.createElement("option");
            opt.value = doc.id;
            opt.textContent = `Dr. ${doc.name || doc.username}`;
            select.appendChild(opt);
        });
    });
}

function loadPatients() {
    const token = localStorage.getItem("token");
    const select = document.getElementById("patient_id");
    if (!select || !token) return;

    fetch(AUTH_URL + "patients/", {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => checkAuth(res))
    .then(data => {
        select.innerHTML = `<option value="">Select Patient</option>`;
        data.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = `${p.name || p.username} (ID: ${p.id})`;
            select.appendChild(opt);
        });
    })
    .catch(err => console.error("Error loading patients:", err));
}

/* ================= CORE WORKFLOW ================= */
function uploadXray() {
    const token = localStorage.getItem("token");
    const image = document.getElementById("image")?.files[0];
    const patient_id = document.getElementById("patient_id")?.value;

    if (!token || !image || !patient_id) return alert("Missing image or patient selection");

    const formData = new FormData();
    formData.append("image", image);
    formData.append("patient_id", patient_id);

    const btn = document.querySelector("button[onclick='uploadXray()']");
    if(btn) { btn.disabled = true; btn.innerText = "Analyzing..."; }

    fetch(BASE_URL + "upload-xray/", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token },
        body: formData
    })
    .then(res => checkAuth(res))
    .then(data => {
        if (data.id) {
            localStorage.setItem("last_report_id", data.id); 
            localStorage.setItem("last_prediction", data.prediction);
            localStorage.setItem("last_confidence", data.confidence);
            localStorage.setItem("last_lime_img", data.lime_image); 
            window.location.href = "result.html";
        }
    })
    .catch(err => alert("Upload failed"))
    .finally(() => { if(btn) { btn.disabled = false; btn.innerText = "Upload & Analyze"; }});
}

function verifyReport() {
    const token = localStorage.getItem("token");
    const reportId = localStorage.getItem("last_report_id"); 
    
    if (!reportId) return alert("No report found to verify.");

    fetch(BASE_URL + `verify-report/${reportId}/`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => checkAuth(res))
    .then(data => {
        alert("✅ Success: Report verified and sent to patient dashboard.");
        window.location.href = "dashboard.html"; // Go back to see updated stats
    })
    .catch(err => {
        console.error(err);
        alert("Failed to verify report.");
    });
}

/* ================= DASHBOARD INITIALIZATION ================= */
function initDashboard() {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    
    if (!token) return;

    const container = document.getElementById("reportsList");

    if (role === "doctor") {
        fetch(BASE_URL + "doctor-dashboard/", {
            headers: { "Authorization": "Bearer " + token }
        })
        .then(res => checkAuth(res))
        .then(data => {
            const reportsElem = document.getElementById("reports");
            const patientsElem = document.getElementById("patients");
            
            if (reportsElem) reportsElem.innerText = data.total_verified_scans || 0;
            if (patientsElem) patientsElem.innerText = data.unique_patients_count || 0;

            if (container) {
                if (!data.recent_activity || data.recent_activity.length === 0) {
                    container.innerHTML = "<p>No verified reports yet.</p>";
                } else {
                    container.innerHTML = ""; 
                    data.recent_activity.forEach(report => {
                        const div = document.createElement("div");
                        div.className = "report-card";
                        div.innerHTML = `
                            <p><b>Patient:</b> ${report.patient_name}</p>
                            <p><b>Result:</b> ${report.result} (${report.confidence}%)</p>
                            <p><b>Status:</b> ✅ Verified</p>
                            <button class="download-btn" onclick="downloadReport(${report.id})">Download PDF</button>
                            <hr>
                        `;
                        container.appendChild(div);
                    });
                }
            }
        })
        .catch(err => console.error("Dashboard Sync Error:", err));

    } else if (role === "patient") {
        const patientId = localStorage.getItem("user_id");
        if (!patientId) return console.error("Patient ID missing");

        fetch(BASE_URL + `patient-reports/${patientId}/`, {
            headers: { "Authorization": "Bearer " + token }
        })
        .then(res => checkAuth(res))
        .then(data => {
            if (container) {
                if (data.length === 0) {
                    container.innerHTML = `<div class="no-data"><p>No verified reports found.</p></div>`;
                } else {
                    container.innerHTML = ""; 
                    data.forEach(report => {
                        const div = document.createElement("div");
                        div.className = "report-card";
                        div.innerHTML = `
                            <p><b>Date:</b> ${report.created_at}</p>
                            <p><b>Diagnosis:</b> ${report.result} (${report.confidence}%)</p>
                            <button class="download-btn" onclick="downloadReport(${report.id})">Download PDF</button>
                            <hr>
                        `;
                        container.appendChild(div);
                    });
                }
            }
        })
        .catch(err => console.error("Error fetching patient reports:", err));
    }
}

function downloadReport(reportId) {
    const token = localStorage.getItem("token");
    fetch(BASE_URL + "download-report/" + reportId + "/", {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.ok ? res.blob() : Promise.reject())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Medical_Report_${reportId}.pdf`;
        a.click();
    })
    .catch(() => alert("Download failed"));
}

/* ================= AUTO-INITIALIZE ================= */
document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    if (path.includes("upload.html")) loadPatients();
    if (path.includes("dashboard.html") || path.includes("reports.html")) initDashboard();
    
    if (path.includes("result.html")) {
        const pred = localStorage.getItem("last_prediction");
        const lime = localStorage.getItem("last_lime_img");
        const conf = localStorage.getItem("last_confidence");

        const resLabel = document.getElementById("resLabel");
        const confLabel = document.getElementById("confLabel");
        const limeImg = document.getElementById("limeResult");

        if (resLabel) resLabel.innerText = "Result: " + (pred || "Processing...");
        if (confLabel) confLabel.innerText = "Confidence: " + (conf || "0") + "%";
        
        if (limeImg && lime) {
            limeImg.src = lime.startsWith('http') ? lime : MEDIA_BASE + lime;
        }
    }
});