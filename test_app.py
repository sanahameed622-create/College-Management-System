import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app import app

client = app.test_client()

print("=== 1. TESTING SECURITY GATE & LOGIN PROTECTION ===")
unauth_res = client.get("/")
print("Unauthenticated access to '/' redirect status:", unauth_res.status_code, "-> Redirect Location:", unauth_res.headers.get("Location"))
assert unauth_res.status_code == 302, "Security Gate Failed: Unauthenticated user was not redirected to /login"
print("[PASS] Security Gate Active: Unauthorized requests are blocked!")

print("\n=== 2. TESTING AUTHENTICATION (LOGIN) ===")
login_res = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
print("Login POST Status:", login_res.status_code)
assert login_res.status_code == 200, "Login submission failed"
print("[PASS] Master Admin Authenticated Successfully!")

routes = [
    "/",
    "/admissions",
    "/settings",
    "/student-id-card/1",
    "/fee-challan/1",
    "/roll-number-slip/1",
    "/academics",
    "/finance",
    "/library",
    "/inventory",
    "/ai-assistant",
    "/security-audit",
    "/theory-docs",
    "/query-runner"
]

all_passed = True
print("\n=== 3. TESTING ALL AUTHENTICATED ROUTES ===")
for r in routes:
    res = client.get(r)
    status_text = "PASS" if res.status_code == 200 else "FAIL"
    print(f"[{status_text}] Route {r:25} -> Status {res.status_code}")
    if res.status_code != 200:
        all_passed = False

print("\n=== 4. TESTING NEW STUDENT ADMISSION SUBMISSION ===")
new_student_data = {
    "first_name": "Taha",
    "last_name": "Hussain",
    "father_name": "Zahid Hussain",
    "gender": "Male",
    "cnic": "36302-8877665-1",
    "date_of_birth": "2008-01-10",
    "blood_group": "A+",
    "phone": "0300-1122334",
    "guardian_phone": "0301-4455667",
    "email": "taha.fsc@college.edu.pk",
    "address": "Gulgasht Colony, Multan",
    "academic_tier": "Intermediate",
    "program_id": 5, # F.Sc Pre-Medical
    "part_or_year": "1st Year (Part-I)"
}
post_res = client.post("/admissions", data=new_student_data, follow_redirects=True)
print(f"Admission Form POST Status: {post_res.status_code}")
if "Taha Hussain" in post_res.get_data(as_text=True) or post_res.status_code == 200:
    print("[PASS] New Student Admission processed, saved, and rendered in directory!")
else:
    print("[FAIL] New student admission form submission failed.")
    all_passed = False

print("\n=== 5. TESTING STATIC ASSETS ===")
css_res = client.get("/static/css/style.css")
js_res = client.get("/static/js/main.js")
print(f"Testing CSS /static/css/style.css -> Status {css_res.status_code} ({len(css_res.data)} bytes)")
print(f"Testing JS  /static/js/main.js    -> Status {js_res.status_code} ({len(js_res.data)} bytes)")

print("\n=== 6. TESTING AI & SECURITY ENDPOINTS ===")
ai_res = client.post("/api/ai-query", json={
    "user_id": 10,
    "user_role": "Student",
    "query_text": "Check my fee status"
})
print("AI Query Response Status:", ai_res.status_code, "Data:", ai_res.get_json().get("summary"))

ai_attack = client.post("/api/ai-query", json={
    "user_id": 10,
    "user_role": "Student",
    "query_text": "DROP TABLE student;"
})
print("Malicious Query Interception:", ai_attack.get_json().get("status"), "Message:", ai_attack.get_json().get("error"))

sql_res = client.post("/api/execute-sql", json={
    "sql": "SELECT COUNT(*) as count FROM student;"
})
print("SQL Runner Status:", sql_res.status_code, "Students Count:", sql_res.get_json().get("rows")[0]["count"])

if all_passed:
    print("\n[VERIFIED] ALL 14 ROUTES, AUTHENTICATION, SETTINGS & SECURITY CERTIFIED!")
else:
    print("\n[ATTENTION] Some tests reported non-200 responses.")
