"""
AcademiaPro Unified Database Engine
Provides clean abstraction for PostgreSQL and SQLite with safe query execution.
"""
import os
import sqlite3
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "academiapro.db")

class DatabaseEngine:
    def __init__(self):
        self.use_postgres = os.environ.get("USE_POSTGRES") == "1"
        self.pg_config = {
            "host": os.environ.get("PGHOST", "localhost"),
            "port": os.environ.get("PGPORT", "5432"),
            "user": os.environ.get("PGUSER", "postgres"),
            "password": os.environ.get("PGPASSWORD", "postgres"),
            "dbname": os.environ.get("PGDATABASE", "academiapro_db")
        }

    def get_connection(self):
        if self.use_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            return psycopg2.connect(**self.pg_config, cursor_factory=RealDictCursor)
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
            else:
                conn.commit()
                result = []
            return result
        finally:
            conn.close()

    def execute(self, sql: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def get_kpis(self) -> Dict[str, Any]:
        """Calculates dashboard metrics."""
        try:
            students_count = self.query("SELECT COUNT(*) as count FROM student WHERE status = 'Active'")[0]['count']
            teachers_count = self.query("SELECT COUNT(*) as count FROM teacher")[0]['count']
            courses_count = self.query("SELECT COUNT(*) as count FROM course")[0]['count']
            defaulters_count = self.query("SELECT COUNT(*) as count FROM v_defaulters")[0]['count']
            low_stock_count = self.query("SELECT COUNT(*) as count FROM v_low_stock")[0]['count']
            overdue_books_count = self.query("SELECT COUNT(*) as count FROM v_overdue_books")[0]['count']
            total_collected = self.query("SELECT COALESCE(SUM(paid_amount), 0.0) as total FROM student_invoice")[0]['total']
            total_receivable = self.query("SELECT COALESCE(SUM(balance_due), 0.0) as total FROM student_invoice")[0]['total']

            return {
                "active_students": students_count,
                "faculty_members": teachers_count,
                "courses": courses_count,
                "defaulters": defaulters_count,
                "low_stock_alerts": low_stock_count,
                "overdue_books": overdue_books_count,
                "fee_collected": f"PKR {total_collected:,.2f}",
                "fee_receivable": f"PKR {total_receivable:,.2f}"
            }
        except Exception as e:
            return {"error": str(e)}

    def execute_safe_ai_query(self, user_id: int, user_role: str, user_query: str, proposed_sql: str) -> Dict[str, Any]:
        clean_sql = proposed_sql.strip()
        upper_sql = clean_sql.upper()

        forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC']
        for kw in forbidden_keywords:
            if upper_sql.startswith(kw) or f" {kw} " in upper_sql:
                self.log_ai_message(user_id, user_role, user_query, proposed_sql, "REJECTED_SECURITY", 0, "Rejected: Security policy permits SELECT only.")
                return {
                    "success": False,
                    "error": "Security Violation: Only read-only SELECT operations on analytical views are permitted.",
                    "status": "REJECTED_SECURITY"
                }

        if not upper_sql.startswith("SELECT"):
            self.log_ai_message(user_id, user_role, user_query, proposed_sql, "REJECTED_SECURITY", 0, "Rejected: Query must begin with SELECT.")
            return {
                "success": False,
                "error": "Query rejected: AI Assistant is strictly restricted to SELECT queries.",
                "status": "REJECTED_SECURITY"
            }

        try:
            results = self.query(clean_sql)
            summary = f"Query executed successfully returning {len(results)} row(s)."
            self.log_ai_message(user_id, user_role, user_query, clean_sql, "SUCCESS", len(results), summary)
            return {
                "success": True,
                "rows": results,
                "row_count": len(results),
                "summary": summary,
                "sql": clean_sql
            }
        except Exception as e:
            self.log_ai_message(user_id, user_role, user_query, clean_sql, "SYNTAX_ERROR", 0, str(e))
            return {
                "success": False,
                "error": str(e),
                "status": "SYNTAX_ERROR",
                "sql": clean_sql
            }

    def log_ai_message(self, user_id: int, role: str, query: str, sql: str, status: str, row_count: int, summary: str):
        try:
            self.execute("""
            INSERT INTO message (conversation_id, user_id, user_role, user_query, generated_sql, execution_status, row_count_returned, response_summary, timestamp)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (user_id, role, query, sql, status, row_count, summary))
        except Exception as err:
            print(f"[!] Warning logging AI message: {err}")

db = DatabaseEngine()
