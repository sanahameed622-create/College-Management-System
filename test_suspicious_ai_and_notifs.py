import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app import app
from security_shield import shield

client = app.test_client()

# Authenticate as Admin first
client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)

print("=== 1. TESTING AI INQUIRY ON SUSPICIOUS ACTIVITY ===")
# Query in Roman Urdu exactly as user specified
queries = [
    "kya koi suspicious activity hwi ha",
    "kya koi attack hua hai",
    "any threats detected today?"
]

for q in queries:
    res = client.post("/api/ai-query", json={
        "user_id": 1,
        "user_role": "Admin",
        "query_text": q
    })
    assert res.status_code == 200, f"Query '{q}' failed with status {res.status_code}"
    data = res.get_json()
    print(f"\nQuery: '{q}'")
    print(f"Summary: {data.get('summary')}")
    print(f"Rows ({len(data.get('rows', []))} items):")
    for row in data.get('rows', []):
        print("  -", row)

print("\n=== 2. TESTING DYNAMIC SECURITY NOTIFICATIONS ===")
# Initially, zero security alerts
notif_res = client.get("/api/notifications/poll")
assert notif_res.status_code == 200
data = notif_res.get_json()
print("Initial Notifications:", data["total_count"], "Security Count:", data["security_count"])

# Simulate a suspicious attack from an IP (5 failed logins)
test_bad_ip = "185.220.101.5"
for i in range(5):
    shield.record_login_attempt(test_bad_ip, f"victim_account_{i}", success=False)

# Check notifications again
notif_res2 = client.get("/api/notifications/poll")
data2 = notif_res2.get_json()
print("\nAfter Attack Auto-Ban:")
print("Updated Total Notifications:", data2["total_count"], "Security Count:", data2["security_count"])
assert data2["security_count"] >= 1, "Expected at least 1 security notification after IP ban"

# Verify the security notification content
sec_alert = [n for n in data2["notifications"] if "CRITICAL_SECURITY" in n["type"]][0]
print("Generated Security Alert Title:", sec_alert["title"])
print("Generated Security Alert Message:", sec_alert["message"])
print("Generated Security Alert Action URL:", sec_alert["action_url"])

# Query AI again during active threat:
print("\n=== 3. TESTING AI QUERY DURING ACTIVE THREAT ===")
res_threat = client.post("/api/ai-query", json={
    "user_id": 1,
    "user_role": "Admin",
    "query_text": "kya koi suspicious activity hwi ha"
})
threat_data = res_threat.get_json()
print("AI Response under Attack:", threat_data.get("summary"))
assert "Alert:" in threat_data.get("summary") or "Suspicious IP" in str(threat_data.get("rows"))

# Clean up test IP
shield.unblock_ip(test_bad_ip)
print("\n[SUCCESS] AI Suspicious Query & Automated Notifications 100% Certified!")
