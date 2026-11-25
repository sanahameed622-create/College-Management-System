import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app import app
from database_engine import db

client = app.test_client()

print("="*60)
print("TESTING ALL USER LOGINS & PERMISSIONS IN ACADEMIAPRO")
print("="*60)

users_to_test = [
    ("admin", "sana123", "Admin"),
    ("prof_tariq", "sana123", "Teacher"),
    ("std_ali_khan", "sana123", "Student"),
    ("2026_fsc_101", "sana123", "Student"),
    ("accountant_bilal", "sana123", "Accountant"),
    ("librarian_ayesha", "sana123", "Librarian"),
    ("store_imran", "sana123", "StoreKeeper"),
    ("parent", "sana123", "Parent"),
]

endpoints_to_test = [
    ("/dashboard", "Admin Dashboard"),
    ("/academics", "Academics Portal"),
    ("/finance", "Finance & Invoicing"),
    ("/inventory", "Inventory & Assets"),
    ("/admissions", "Admissions Desk"),
    ("/settings", "Institutional Settings"),
    ("/security-audit", "Security Audit Log"),
    ("/student-desk", "Student Desk (General)"),
    ("/student-desk/std_ali_khan", "Ali Khan Student Desk"),
    ("/student-desk/2026_fsc_101", "Hamza Rehman Student Desk"),
    ("/student-id-card/std_ali_khan", "Student ID Card"),
    ("/fee-challan/std_ali_khan", "Student Fee Challan"),
    ("/roll-number-slip/std_ali_khan", "Roll Number Slip"),
]

for username, password, expected_role in users_to_test:
    print(f"\n--- Testing User: '{username}' (Role: {expected_role}) ---")
    
    # Reset session with fresh client
    c = app.test_client()
    
    # 1. Login
    login_res = c.post("/login", data={
        "username": username,
        "password": password,
        "slider_token": "dummy_test_pass"
    }, follow_redirects=False)
    
    status = login_res.status_code
    location = login_res.headers.get("Location", "")
    print(f"Login Response: Status {status} -> Redirects to: {location}")
    
    # Now follow redirect
    follow_res = c.get(location) if location else None
    if follow_res:
        print(f"Landed on: '{location}' with Status Code {follow_res.status_code}")
        if follow_res.status_code == 500:
            print(f"  [ERROR 500] on landing page {location}!")
    
    # Test specific routes access for this role
    print("Testing endpoint access permissions:")
    for ep, label in endpoints_to_test:
        r = c.get(ep, follow_redirects=False)
        r_status = r.status_code
        r_loc = r.headers.get("Location", "")
        
        # Check if 500
        if r_status == 500:
            print(f"  [CRITICAL ERROR 500] {ep} ({label})")
        elif r_status == 200:
            print(f"  [200 ALLOWED] {ep} ({label})")
        elif r_status in (301, 302):
            print(f"  [{r_status} REDIRECT] {ep} -> {r_loc}")
        elif r_status == 403:
            print(f"  [403 BLOCKED] {ep} ({label})")
        else:
            print(f"  [{r_status}] {ep}")

print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60)
