"""
Unit & Integration Tests for AcademiaPro Security Shield
Tests:
1. CAPTCHA generation and validation
2. Suspicious IP Tracking & Automated 403 Blacklisting
3. Sliding-window IP Rate Limiting (429 Too Many Requests)
4. Account-based Brute-Force Throttling & Account Lockout
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app import app
from security_shield import shield

print("============================================================")
print("  ACADEMIAPRO - ADVANCED SECURITY DEFENSE VERIFICATION")
print("============================================================")

client = app.test_client()

# TEST 1: SLIDER VERIFICATION CHALLENGE & VALIDATION
print("\n[TEST 1] Verifying Interactive Anti-Bot Slider Challenge Engine...")
stoken = shield.generate_slider_challenge()
print(f"Generated Slider Token: '{stoken}'")
assert shield.verify_slider_token(stoken, stoken) is True, "Expected matching slider token to pass"
assert shield.verify_slider_token(stoken, "fake_token_123") is False, "Expected wrong token to fail"
assert shield.verify_slider_token(stoken, "") is False, "Expected empty token to fail"
print("[PASS] Interactive Slider Verification Validated!")

# TEST 2: ACCOUNT-BASED BRUTE-FORCE THROTTLING
print("\n[TEST 2] Verifying Account-Based Brute-Force Throttling & Lockout...")
test_user = "test_attacker_target"
shield.unlock_account(test_user)

# Simulate 4 failed attempts
for i in range(1, 5):
    shield.record_login_attempt("192.168.1.100", test_user, success=False)
    is_locked, remaining, count = shield.check_account_status(test_user)
    assert is_locked is False, f"Account should not be locked at attempt {i}"
    print(f"  Attempt {i}: Failed recorded. Account locked = False (Attempts: {count}/5)")

# 5th failed attempt -> Must trigger lockout
shield.record_login_attempt("192.168.1.100", test_user, success=False)
is_locked, remaining, count = shield.check_account_status(test_user)
assert is_locked is True, "Account should be LOCKED after 5th consecutive failure"
print(f"  Attempt 5: [LOCKED] Account '{test_user}' locked for ~{remaining // 60 + 1} minutes!")

# Test admin unlock
assert shield.unlock_account(test_user) is True
is_locked, _, _ = shield.check_account_status(test_user)
assert is_locked is False, "Account should be unlocked after admin action"
print("[PASS] Account-Based Throttling & Admin Unlock Verified!")

# TEST 3: SUSPICIOUS IP AUTO-BLOCKING
print("\n[TEST 3] Verifying Suspicious IP Auto-Blacklisting (403 Defense)...")
bad_ip = "198.51.100.42"
shield.unblock_ip(bad_ip)

for i in range(1, 5):
    shield.record_login_attempt(bad_ip, f"victim_{i}", success=False)
    is_blocked, _, _ = shield.check_ip_status(bad_ip)
    assert is_blocked is False

# 5th failed attempt from this IP -> Trigger auto-ban
shield.record_login_attempt(bad_ip, "victim_5", success=False)
is_blocked, reason, rem = shield.check_ip_status(bad_ip)
assert is_blocked is True, "Suspicious IP should be automatically blacklisted"
print(f"  Suspicious IP {bad_ip} Auto-Banned! Reason: '{reason}', Cooldown: ~{rem // 60 + 1} mins")

# Verify HTTP layer blocks this IP with 403
blocked_res = client.get("/", environ_overrides={"REMOTE_ADDR": bad_ip})
print(f"  HTTP Request from {bad_ip} -> Status Code: {blocked_res.status_code}")
assert blocked_res.status_code == 403, "Blocked IP should receive HTTP 403 Forbidden"
assert "Suspended" in blocked_res.get_data(as_text=True)

# Admin unblock IP
shield.unblock_ip(bad_ip)
unblocked_is_blocked, _, _ = shield.check_ip_status(bad_ip)
assert unblocked_is_blocked is False, "IP should be released after unblock"
print("[PASS] Suspicious IP Auto-Ban, 403 Block Page & Admin Release Verified!")

# TEST 4: RATE LIMITING (SLIDING WINDOW)
print("\n[TEST 4] Verifying Request Rate Limiting (429 Defense)...")
spam_ip = "203.0.113.88"
# Directly test shield rate limit
for req_num in range(1, 121):
    allowed, _ = shield.check_rate_limit(spam_ip, is_auth_endpoint=False)
    assert allowed is True

# 121st request -> Rate limit hit
allowed, retry_after = shield.check_rate_limit(spam_ip, is_auth_endpoint=False)
assert allowed is False, "Request over 120/min should be throttled"
assert retry_after > 0
print(f"  Rate Limit Triggered: Allowed={allowed}, Retry-After={retry_after}s")
print("[PASS] Sliding-Window Rate Limiting Engine Verified!")

# TEST 5: SECURITY AUDIT TELEMETRY
print("\n[TEST 5] Verifying Security Dashboard Telemetry Integration...")
summary = shield.get_dashboard_summary()
print("  Total Screened Requests:", summary["metrics"]["total_screened_requests"])
print("  Rate Limit Hits:", summary["metrics"]["rate_limit_hits"])
print("  IP Blocks Enacted:", summary["metrics"]["ip_blocks_enacted"])
print("  Account Locks Enacted:", summary["metrics"]["account_locks_enacted"])
print("  Captcha Challenges Served:", summary["metrics"]["captcha_challenges_served"])
assert summary["metrics"]["total_screened_requests"] > 0
print("[PASS] Forensic Telemetry & Dashboard Integration Verified!")

print("\n============================================================")
print("  [SUCCESS] ALL 4 ADVANCED SECURITY LAYERS FULLY CERTIFIED!")
print("============================================================")
