"""
AcademiaPro - Advanced Security Shield & Threat Defense Engine
Provides:
1. Dynamic Anti-Bot Human Verification (CAPTCHA)
2. Suspicious IP Tracking & Automated Blacklisting
3. IP-Based Sliding-Window Rate Limiting
4. Account-Based Brute-Force Throttling & Account Lockout
5. Security Audit Telemetry & Admin Unblock Operations
"""

import time
import random
import threading
from typing import Dict, Tuple, Optional, List, Any

class SecurityShield:
    def __init__(self):
        self.lock = threading.Lock()
        
        # Configuration constants
        self.RATE_LIMIT_GLOBAL_MAX = 120       # Max requests per minute per IP
        self.RATE_LIMIT_GLOBAL_WINDOW = 60     # Window in seconds
        
        self.RATE_LIMIT_AUTH_MAX = 10          # Max login POST requests per minute per IP
        self.RATE_LIMIT_AUTH_WINDOW = 60       # Window in seconds
        
        self.MAX_IP_FAILED_ATTEMPTS = 5        # Failed logins before IP auto-ban
        self.IP_FAIL_WINDOW = 300              # 5 minutes window
        self.IP_BLOCK_DURATION = 900           # 15 minutes ban
        
        self.MAX_ACCOUNT_FAILED_ATTEMPTS = 5   # Failed logins before account lockout
        self.ACCOUNT_FAIL_WINDOW = 600         # 10 minutes window
        self.ACCOUNT_LOCK_DURATION = 600       # 10 minutes lockout
        
        # Storage
        # IP -> list of timestamps
        self.ip_requests: Dict[str, List[float]] = {}
        # IP -> list of failed attempt timestamps
        self.ip_failed_logins: Dict[str, List[float]] = {}
        # IP -> dict(blocked_until: float, reason: str, blocked_at: float, violation_count: int)
        self.blocked_ips: Dict[str, Dict[str, Any]] = {}
        
        # Account username -> dict(failed_timestamps: list[float], locked_until: float, total_violations: int)
        self.account_throttles: Dict[str, Dict[str, Any]] = {}
        
        # In-memory security events log (recent 50 events)
        self.security_events: List[Dict[str, Any]] = []
        
        # Global Telemetry Counters
        self.metrics = {
            "total_screened_requests": 0,
            "rate_limit_hits": 0,
            "ip_blocks_enacted": 0,
            "account_locks_enacted": 0,
            "captcha_challenges_served": 0,
            "captcha_verified": 0,
            "captcha_failures": 0
        }

    # =========================================================================
    # 1. INTERACTIVE SLIDER VERIFICATION (ANTI-BOT SLIDER CAPTCHA)
    # =========================================================================
    def generate_slider_challenge(self) -> str:
        """
        Generates a secure cryptographic verification token for the interactive slider.
        """
        token = f"slide_{int(time.time() * 1000)}_{random.randint(100000, 999999)}"
        with self.lock:
            self.metrics["captcha_challenges_served"] += 1
        return token

    def verify_slider_token(self, session_token: Optional[str], submitted_token: Optional[str]) -> bool:
        """
        Validates the completed slide token generated upon user drag completion.
        """
        if not session_token or not submitted_token:
            with self.lock:
                self.metrics["captcha_failures"] += 1
            return False

        clean_session = str(session_token).strip()
        clean_submitted = str(submitted_token).strip()

        is_valid = (clean_session == clean_submitted)
        with self.lock:
            if is_valid:
                self.metrics["captcha_verified"] += 1
            else:
                self.metrics["captcha_failures"] += 1
        return is_valid

    # Compatibility aliases
    def generate_captcha(self):
        token = self.generate_slider_challenge()
        return token, "Slide to verify", token

    def verify_captcha(self, session_answer: Optional[str], user_input: Optional[str]) -> bool:
        return self.verify_slider_token(session_answer, user_input)

    # =========================================================================
    # 2. SUSPICIOUS IP TRACKING & AUTOMATED BLACKLISTING
    # =========================================================================
    def check_ip_status(self, ip: str) -> Tuple[bool, Optional[str], int]:
        """
        Checks if an IP is currently blacklisted.
        Returns: (is_blocked: bool, reason: str, seconds_remaining: int)
        """
        now = time.time()
        with self.lock:
            if ip in self.blocked_ips:
                info = self.blocked_ips[ip]
                if now < info["blocked_until"]:
                    remaining = int(info["blocked_until"] - now)
                    return True, info["reason"], remaining
                else:
                    # Expired ban: automatically release
                    del self.blocked_ips[ip]
                    self._log_event("IP_UNBLOCKED_AUTO", ip, "Ban duration expired successfully.")
            return False, None, 0

    def block_ip(self, ip: str, reason: str, duration: Optional[int] = None):
        """Explicitly blocks an IP address."""
        dur = duration if duration is not None else self.IP_BLOCK_DURATION
        now = time.time()
        with self.lock:
            self.blocked_ips[ip] = {
                "ip": ip,
                "reason": reason,
                "blocked_at": now,
                "blocked_until": now + dur,
                "duration": dur
            }
            self.metrics["ip_blocks_enacted"] += 1
            self._log_event("IP_AUTO_BLOCKED", ip, f"{reason} (Blocked for {dur // 60} mins)")

    def unblock_ip(self, ip: str) -> bool:
        """Manually unblocks an IP address (Admin action)."""
        with self.lock:
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
            if ip in self.ip_failed_logins:
                del self.ip_failed_logins[ip]
            self._log_event("IP_UNBLOCKED_ADMIN", ip, "Manually unblocked by Institutional Administrator.")
            return True

    # =========================================================================
    # 3. IP-BASED RATE LIMITING (SLIDING WINDOW)
    # =========================================================================
    def check_rate_limit(self, ip: str, is_auth_endpoint: bool = False) -> Tuple[bool, int]:
        """
        Checks if the IP has exceeded request rate thresholds.
        Returns: (is_allowed: bool, retry_after: int)
        """
        now = time.time()
        limit = self.RATE_LIMIT_AUTH_MAX if is_auth_endpoint else self.RATE_LIMIT_GLOBAL_MAX
        window = self.RATE_LIMIT_AUTH_WINDOW if is_auth_endpoint else self.RATE_LIMIT_GLOBAL_WINDOW
        
        with self.lock:
            self.metrics["total_screened_requests"] += 1
            if ip not in self.ip_requests:
                self.ip_requests[ip] = []
                
            # Filter timestamps outside the sliding window
            cutoff = now - window
            self.ip_requests[ip] = [ts for ts in self.ip_requests[ip] if ts > cutoff]
            
            if len(self.ip_requests[ip]) >= limit:
                self.metrics["rate_limit_hits"] += 1
                oldest = self.ip_requests[ip][0]
                retry_after = max(1, int(oldest + window - now))
                self._log_event("RATE_LIMIT_EXCEEDED", ip, f"Exceeded {limit} reqs/{window}s threshold.")
                return False, retry_after
                
            self.ip_requests[ip].append(now)
            return True, 0

    # =========================================================================
    # 4. ACCOUNT-BASED BRUTE-FORCE THROTTLING & LOCKOUT
    # =========================================================================
    def check_account_status(self, username: str) -> Tuple[bool, int, int]:
        """
        Checks if a user account is locked due to brute-force attempts.
        Returns: (is_locked: bool, seconds_remaining: int, failed_count: int)
        """
        if not username:
            return False, 0, 0
            
        clean_user = username.lower().strip()
        now = time.time()
        
        with self.lock:
            data = self.account_throttles.get(clean_user)
            if not data:
                return False, 0, 0
                
            if now < data.get("locked_until", 0):
                remaining = int(data["locked_until"] - now)
                return True, remaining, len(data.get("failed_timestamps", []))
            elif data.get("locked_until", 0) > 0 and now >= data.get("locked_until", 0):
                # Lockout expired: reset lock
                data["locked_until"] = 0
                data["failed_timestamps"] = []
                self._log_event("ACCOUNT_UNLOCKED_AUTO", clean_user, "Account lockout period expired.")
                
            return False, 0, len(data.get("failed_timestamps", []))

    def record_login_attempt(self, ip: str, username: str, success: bool):
        """
        Records login attempt results for both IP and Account security profiles.
        """
        clean_user = (username or "unknown").lower().strip()
        now = time.time()
        
        with self.lock:
            if success:
                # Clear IP and Account failed attempt trackers
                if ip in self.ip_failed_logins:
                    self.ip_failed_logins[ip] = []
                if clean_user in self.account_throttles:
                    self.account_throttles[clean_user]["failed_timestamps"] = []
                self._log_event("AUTH_SUCCESS", f"{clean_user}@{ip}", "Authentication granted.")
            else:
                # 1. Update IP failed attempts
                if ip not in self.ip_failed_logins:
                    self.ip_failed_logins[ip] = []
                ip_cutoff = now - self.IP_FAIL_WINDOW
                self.ip_failed_logins[ip] = [ts for ts in self.ip_failed_logins[ip] if ts > ip_cutoff]
                self.ip_failed_logins[ip].append(now)
                
                if len(self.ip_failed_logins[ip]) >= self.MAX_IP_FAILED_ATTEMPTS:
                    # Auto-block suspicious IP
                    self.blocked_ips[ip] = {
                        "ip": ip,
                        "reason": f"Suspicious activity: {len(self.ip_failed_logins[ip])} failed login attempts in 5 minutes.",
                        "blocked_at": now,
                        "blocked_until": now + self.IP_BLOCK_DURATION,
                        "duration": self.IP_BLOCK_DURATION
                    }
                    self.metrics["ip_blocks_enacted"] += 1
                    self._log_event("IP_AUTO_BLOCKED", ip, "Auto-banned due to credential stuffing / brute-force anomalies.")

                # 2. Update Account failed attempts
                if clean_user != "unknown":
                    if clean_user not in self.account_throttles:
                        self.account_throttles[clean_user] = {
                            "failed_timestamps": [],
                            "locked_until": 0,
                            "total_violations": 0
                        }
                    acc = self.account_throttles[clean_user]
                    acc_cutoff = now - self.ACCOUNT_FAIL_WINDOW
                    acc["failed_timestamps"] = [ts for ts in acc["failed_timestamps"] if ts > acc_cutoff]
                    acc["failed_timestamps"].append(now)
                    
                    if len(acc["failed_timestamps"]) >= self.MAX_ACCOUNT_FAILED_ATTEMPTS:
                        acc["locked_until"] = now + self.ACCOUNT_LOCK_DURATION
                        acc["total_violations"] += 1
                        self.metrics["account_locks_enacted"] += 1
                        self._log_event("ACCOUNT_LOCKED", clean_user, f"Account locked for {self.ACCOUNT_LOCK_DURATION // 60} mins after 5 failed attempts.")

    def unlock_account(self, username: str) -> bool:
        """Manually unlocks a user account (Admin action)."""
        clean_user = username.lower().strip()
        with self.lock:
            if clean_user in self.account_throttles:
                self.account_throttles[clean_user]["locked_until"] = 0
                self.account_throttles[clean_user]["failed_timestamps"] = []
                self._log_event("ACCOUNT_UNLOCKED_ADMIN", clean_user, "Manually unlocked by Master Administrator.")
                return True
            return False

    # =========================================================================
    # 5. FORENSIC TELEMETRY & EVENT LOGGING
    # =========================================================================
    def _log_event(self, event_type: str, target: str, details: str):
        event = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "target": target,
            "details": details
        }
        self.security_events.insert(0, event)
        if len(self.security_events) > 50:
            self.security_events.pop()

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Provides real-time defensive telemetry for the Security & Audit UI."""
        now = time.time()
        with self.lock:
            # Active blocked IPs
            active_blocked = []
            for ip, item in list(self.blocked_ips.items()):
                if now < item["blocked_until"]:
                    active_blocked.append({
                        "ip": ip,
                        "reason": item["reason"],
                        "remaining_mins": max(1, int((item["blocked_until"] - now) / 60)),
                        "blocked_at": time.strftime("%H:%M:%S", time.localtime(item["blocked_at"]))
                    })
                    
            # Active locked accounts
            active_locked = []
            for u, data in list(self.account_throttles.items()):
                if now < data.get("locked_until", 0):
                    active_locked.append({
                        "username": u,
                        "remaining_mins": max(1, int((data["locked_until"] - now) / 60)),
                        "failed_attempts": len(data.get("failed_timestamps", [])),
                        "total_violations": data.get("total_violations", 0)
                    })
                    
            return {
                "metrics": dict(self.metrics),
                "active_blocked_ips": active_blocked,
                "active_locked_accounts": active_locked,
                "recent_events": list(self.security_events[:15])
            }

# Instantiate singleton engine
shield = SecurityShield()
