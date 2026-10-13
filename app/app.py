"""
AcademiaPro - Flask Application Server
Integrated College Management System
"""
import os
import json
from flask import Flask, render_template, request, jsonify
from database_engine import db

app = Flask(__name__)
app.secret_key = "academiapro_secret_salt_2026"

@app.route("/")
def dashboard():
    kpis = db.get_kpis()
    defaulters = db.query("SELECT * FROM v_defaulters LIMIT 5")
    low_stock = db.query("SELECT * FROM v_low_stock LIMIT 5")
    overdue_books = db.query("SELECT * FROM v_overdue_books LIMIT 5")
    attendance_alerts = db.query("SELECT * FROM v_attendance_shortage WHERE examination_eligibility = 'DEBARRED_FROM_FINAL_EXAM' LIMIT 5")
    return render_template("index.html", 
                           kpis=kpis, 
                           defaulters=defaulters, 
                           low_stock=low_stock, 
                           overdue_books=overdue_books,
                           attendance_alerts=attendance_alerts)

@app.route("/academics")
def academics():
    departments = db.query("SELECT * FROM department")
    programs = db.query("SELECT p.*, d.dept_name FROM program p JOIN department d ON p.dept_id = d.dept_id")
    courses = db.query("SELECT c.*, p.program_code FROM course c JOIN program p ON c.program_id = p.program_id")
    sections = db.query("""
        SELECT sec.*, c.course_code, c.title as course_title, t.first_name || ' ' || t.last_name as teacher_name 
        FROM section sec 
        JOIN course c ON sec.course_id = c.course_id 
        JOIN teacher t ON sec.teacher_id = t.teacher_id
    """)
    students = db.query("""
        SELECT s.*, p.program_code 
        FROM student s 
        JOIN program p ON s.program_id = p.program_id 
        ORDER BY s.student_id ASC
    """)
    transcripts = db.query("SELECT * FROM v_student_transcript ORDER BY student_id, course_code")
    attendance_report = db.query("SELECT * FROM v_attendance_shortage")
    return render_template("academics.html",
                           departments=departments,
                           programs=programs,
                           courses=courses,
                           sections=sections,
                           students=students,
                           transcripts=transcripts,
                           attendance_report=attendance_report)

@app.route("/finance")
def finance():
    fee_structures = db.query("""
        SELECT fs.*, p.program_name, sem.term_name || ' ' || sem.academic_year as semester_term 
        FROM fee_structure fs 
        JOIN program p ON fs.program_id = p.program_id 
        JOIN semester sem ON fs.semester_id = sem.semester_id
    """)
    invoices = db.query("""
        SELECT inv.*, s.roll_number, s.first_name || ' ' || s.last_name as student_name 
        FROM student_invoice inv 
        JOIN student s ON inv.student_id = s.student_id 
        ORDER BY inv.invoice_id DESC
    """)
    payments = db.query("""
        SELECT p.*, inv.invoice_number, s.roll_number, s.first_name || ' ' || s.last_name as student_name
        FROM fee_payment p
        JOIN student_invoice inv ON p.invoice_id = inv.invoice_id
        JOIN student s ON inv.student_id = s.student_id
        ORDER BY p.payment_id DESC
    """)
    fines = db.query("""
        SELECT fn.*, s.roll_number, s.first_name || ' ' || s.last_name as student_name
        FROM fine fn
        JOIN student s ON fn.student_id = s.student_id
        ORDER BY fn.fine_id DESC
    """)
    defaulters = db.query("SELECT * FROM v_defaulters")
    return render_template("finance.html",
                           fee_structures=fee_structures,
                           invoices=invoices,
                           payments=payments,
                           fines=fines,
                           defaulters=defaulters)

@app.route("/library")
def library():
    books = db.query("SELECT * FROM book ORDER BY book_id ASC")
    copies = db.query("""
        SELECT bc.*, b.title as book_title, b.isbn, b.author 
        FROM book_copy bc 
        JOIN book b ON bc.book_id = b.book_id
    """)
    members = db.query("""
        SELECT lm.*, ua.full_name, ua.email 
        FROM library_member lm 
        JOIN user_account ua ON lm.user_id = ua.user_id
    """)
    issues = db.query("""
        SELECT bi.*, b.title as book_title, bc.barcode, ua.full_name as member_name, lm.membership_number 
        FROM book_issue bi 
        JOIN book_copy bc ON bi.copy_id = bc.copy_id 
        JOIN book b ON bc.book_id = b.book_id 
        JOIN library_member lm ON bi.member_id = lm.member_id 
        JOIN user_account ua ON lm.user_id = ua.user_id
        ORDER BY bi.issue_id DESC
    """)
    overdue_books = db.query("SELECT * FROM v_overdue_books")
    return render_template("library.html",
                           books=books,
                           copies=copies,
                           members=members,
                           issues=issues,
                           overdue_books=overdue_books)

@app.route("/inventory")
def inventory():
    categories = db.query("SELECT * FROM item_category")
    rooms = db.query("""
        SELECT r.*, d.dept_name, d.dept_code 
        FROM room_lab r 
        JOIN department d ON r.dept_id = d.dept_id
    """)
    items = db.query("""
        SELECT itm.*, cat.category_name 
        FROM inventory_item itm 
        JOIN item_category cat ON itm.category_id = cat.category_id
    """)
    issuances = db.query("""
        SELECT isi.*, itm.item_name, itm.item_code, r.room_number, ua.full_name as issued_to_name
        FROM item_issuance isi
        JOIN inventory_item itm ON isi.item_id = itm.item_id
        JOIN room_lab r ON isi.room_id = r.room_id
        JOIN user_account ua ON isi.issued_to_user_id = ua.user_id
        ORDER BY isi.issuance_id DESC
    """)
    low_stock = db.query("SELECT * FROM v_low_stock")
    return render_template("inventory.html",
                           categories=categories,
                           rooms=rooms,
                           items=items,
                           issuances=issuances,
                           low_stock=low_stock)

@app.route("/ai-assistant")
def ai_assistant():
    conversations = db.query("SELECT * FROM conversation ORDER BY conversation_id DESC")
    messages = db.query("""
        SELECT m.*, ua.full_name 
        FROM message m 
        JOIN user_account ua ON m.user_id = ua.user_id 
        ORDER BY m.message_id DESC LIMIT 20
    """)
    return render_template("ai_assistant.html", conversations=conversations, messages=messages)

@app.route("/security-audit")
def security_audit():
    users = db.query("""
        SELECT u.*, r.role_name 
        FROM user_account u 
        LEFT JOIN user_role ur ON u.user_id = ur.user_id 
        LEFT JOIN role r ON ur.role_id = r.role_id
        ORDER BY u.user_id ASC
    """)
    roles = db.query("SELECT * FROM role")
    audit_logs = db.query("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT 50")
    return render_template("security_audit.html", users=users, roles=roles, audit_logs=audit_logs)

@app.route("/theory-docs")
def theory_docs():
    return render_template("theory_docs.html")

@app.route("/query-runner")
def query_runner():
    return render_template("query_runner.html")

@app.route("/api/ai-query", methods=["POST"])
def api_ai_query():
    data = request.get_json() or {}
    user_id = int(data.get("user_id", 10))
    user_role = data.get("user_role", "Student")
    query_text = data.get("query_text", "")
    query_lower = query_text.lower()
    sql = ""

    upper_query = query_text.strip().upper()
    direct_sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE']
    if any(upper_query.startswith(kw) for kw in direct_sql_keywords):
        sql = query_text.strip()
    elif "fee" in query_lower or "invoice" in query_lower or "due" in query_lower or "balance" in query_lower:
        if user_role == "Student":
            sql = f"SELECT invoice_number, total_amount, paid_amount, balance_due, status FROM student_invoice WHERE student_id = {user_id - 9};"
        else:
            sql = "SELECT * FROM v_defaulters;"
    elif "transcript" in query_lower or "grade" in query_lower or "gpa" in query_lower or "result" in query_lower:
        if user_role == "Student":
            sql = f"SELECT course_code, course_title, final_grade, gpa_points, quality_points FROM v_student_transcript WHERE student_id = {user_id - 9};"
        else:
            sql = "SELECT roll_number, student_name, course_code, course_title, final_grade, gpa_points FROM v_student_transcript LIMIT 25;"
    elif "attendance" in query_lower or "shortage" in query_lower or "debarred" in query_lower:
        if user_role == "Student":
            sql = f"SELECT course_code, course_title, total_lectures_held, attended_lectures, attendance_percentage, examination_eligibility FROM v_attendance_shortage WHERE student_id = {user_id - 9};"
        else:
            sql = "SELECT * FROM v_attendance_shortage WHERE examination_eligibility = 'DEBARRED_FROM_FINAL_EXAM';"
    elif "book" in query_lower or "overdue" in query_lower or "library" in query_lower:
        sql = "SELECT * FROM v_overdue_books;"
    elif "stock" in query_lower or "inventory" in query_lower or "reorder" in query_lower:
        sql = "SELECT * FROM v_low_stock;"
    elif "student" in query_lower or "enrollment" in query_lower:
        sql = "SELECT student_id, roll_number, first_name, last_name, email, current_semester_num, status FROM student LIMIT 15;"
    else:
        sql = data.get("custom_sql", "SELECT * FROM v_student_transcript LIMIT 10;")

    execution_result = db.execute_safe_ai_query(user_id, user_role, query_text, sql)
    return jsonify(execution_result)

@app.route("/api/execute-sql", methods=["POST"])
def api_execute_sql():
    data = request.get_json() or {}
    sql = data.get("sql", "").strip()
    if not sql:
        return jsonify({"success": False, "error": "SQL string cannot be empty."})

    if not sql.upper().startswith("SELECT") and not sql.upper().startswith("WITH") and not sql.upper().startswith("EXPLAIN"):
        return jsonify({"success": False, "error": "Safety Protocol: Only SELECT / WITH analytical queries are permitted in this runner."})

    try:
        results = db.query(sql)
        return jsonify({
            "success": True,
            "rows": results,
            "row_count": len(results),
            "columns": list(results[0].keys()) if results else []
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Starting AcademiaPro Web Application on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
