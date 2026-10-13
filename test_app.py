import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app import app

client = app.test_client()

routes = [
    "/",
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
for r in routes:
    res = client.get(r)
    print(f"Testing route {r:20} -> Status {res.status_code}")
    if res.status_code != 200:
        all_passed = False

if all_passed:
    print("\n[SUCCESS] All routes rendered with HTTP 200 OK!")
else:
    print("\n[FAIL] Some routes failed.")

print("\n--- Testing Static Assets ---")
css_res = client.get("/static/css/style.css")
js_res = client.get("/static/js/main.js")
print(f"Testing CSS /static/css/style.css -> Status {css_res.status_code} ({len(css_res.data)} bytes)")
print(f"Testing JS  /static/js/main.js    -> Status {js_res.status_code} ({len(js_res.data)} bytes)")

# Test AI safe query
print("\n--- Testing API Endpoints ---")
ai_res = client.post("/api/ai-query", json={
    "user_id": 10,
    "user_role": "Student",
    "query_text": "Check my fee status"
})
print("AI Query Response Status:", ai_res.status_code, "Data:", ai_res.get_json().get("summary"))

# Test Security rejection on malicious query
ai_attack = client.post("/api/ai-query", json={
    "user_id": 10,
    "user_role": "Student",
    "query_text": "DROP TABLE student;"
})
print("Malicious Query Interception:", ai_attack.get_json().get("status"), "Message:", ai_attack.get_json().get("error"))

# Test SQL runner
sql_res = client.post("/api/execute-sql", json={
    "sql": "SELECT COUNT(*) as count FROM student;"
})
print("SQL Runner Status:", sql_res.status_code, "Rows:", sql_res.get_json().get("rows"))
