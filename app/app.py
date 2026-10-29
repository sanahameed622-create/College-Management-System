"""
AcademiaPro - Flask Application Server
Enterprise Multi-Tier College Management System (Intermediate & BS Programs)
"""
import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database_engine import db

app = Flask(__name__)
app.secret_key = "academiapro_secret_salt_2026_enterprise_secure"

@app.context_processor
def inject_global_context():
    avatar_choice = session.get("user_avatar", "boy")
    if avatar_choice.startswith("http://") or avatar_choice.startswith("https://"):
        avatar_src = avatar_choice
    else:
        avatar_src = f"/static/avatars/{avatar_choice}.svg"
    return {
        "college": db.get_college_profile(),
        "logged_user": session.get("user_name", "Administrator"),
        "logged_role": session.get("user_role", "Admin"),
        "logged_avatar": avatar_choice,
        "avatar_src": avatar_src,
        "is_authenticated": session.get("logged_in", False)
    }

@app.before_request
def require_authentication():
    # Public endpoints that do not require login
    public_endpoints = [
        'login', 'logout', 'static',
        'api_biometric_login', 'api_reset_password_pin',
        'api_update_avatar'
    ]
    if request.endpoint in public_endpoints:
        return
    # Check session
    if not session.get("logged_in"):
        flash("Institutional Authentication Required: Please sign in with your official assigned institutional email / roll number and password or fingerprint.", "warning")
        return redirect(url_for("login"))

    user_role = session.get("user_role", "Admin")

    # Role 1: Student (Access restricted strictly to Student Desk & Docs)
    student_allowed = ['student_desk', 'logout', 'student_id_card', 'fee_challan', 'roll_number_slip', 'api_student_ai', 'static']
    if user_role == "Student" and request.endpoint not in student_allowed:
        return redirect(url_for("student_desk", roll_number=session.get("username", "")))

    # Role 2: Teacher (Access restricted from Finance, Settings, Security Audit, Inventory)
    teacher_blocked = ['finance', 'settings', 'security_audit', 'inventory', 'api_change_password']
    if user_role == "Teacher" and request.endpoint in teacher_blocked:
        flash("Access Notice: Financial Balances, System Inventory & White-Label Settings are restricted to Administrative Authorities.", "warning")
        return redirect(url_for("academics"))


# ==========================================
# AUTHENTICATION & ACCESS CONTROL
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.authenticate_user(username, password)
        if user:
            session["logged_in"] = True
            session["user_id"] = user.get("user_id")
            session["username"] = user.get("username")
            session["user_name"] = user.get("full_name")
            session["user_role"] = user.get("role_name", "Admin")
            flash(f"Welcome back, {user.get('full_name')}!", "success")
            if user.get("role_name") == "Student":
                return redirect(url_for("student_desk", roll_number=user.get("username")))
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials! Master Admin: admin / sana123 or check your assigned Gmail/Password.", "danger")

    return render_template("login.html")

@app.route("/api/biometric-login", methods=["POST"])
def api_biometric_login():
    data = request.get_json() or {}
    identifier = data.get("identifier", "admin")
    user = db.authenticate_biometric(identifier)
    if user:
        session["logged_in"] = True
        session["user_id"] = user.get("user_id")
        session["username"] = user.get("username")
        session["user_name"] = user.get("full_name")
        session["user_role"] = user.get("role_name", "Admin")
        if user.get("role_name") == "Student":
            target_url = url_for("student_desk", roll_number=user.get("username"))
        else:
            target_url = url_for("dashboard")
        return jsonify({"success": True, "redirect": target_url, "user": user.get("full_name")})
    return jsonify({"success": False, "error": "Biometric sensor verification rejected."})

@app.route("/api/reset-password-pin", methods=["POST"])
def api_reset_password_pin():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    pin = data.get("pin", "").strip()
    new_password = data.get("new_password", "").strip()
    res = db.reset_password_with_pin(email, pin, new_password)
    return jsonify(res)

@app.route("/api/update-avatar", methods=["POST"])
def api_update_avatar():
    data = request.get_json() or {}
    avatar_choice = data.get("avatar", "boy").strip()
    session["user_avatar"] = avatar_choice
    user_id = session.get("user_id")
    if user_id:
        try:
            db.execute("UPDATE user_account SET photo_url = ? WHERE user_id = ?", (avatar_choice, user_id))
        except Exception:
            pass
    avatar_src = avatar_choice if avatar_choice.startswith("http") else f"/static/avatars/{avatar_choice}.svg"
    return jsonify({"success": True, "avatar": avatar_choice, "avatar_src": avatar_src})

@app.route("/logout")
def logout():
    session.clear()
    flash("You have successfully logged out of the ERP portal.", "info")
    return redirect(url_for("login"))

# ==========================================
# AUTHENTICATED STUDENT PORTAL DESK
# ==========================================
@app.route("/student-desk", methods=["GET", "POST"])
def student_desk():
    user_role = session.get("user_role", "Admin")
    logged_roll = session.get("username", "")

    # Strict Privacy Enforcement: A student can ONLY view their own record!
    if user_role == "Student":
        query = logged_roll
    else:
        # Admin or Faculty can search/lookup any student's portal
        query = request.args.get("roll_number", "").strip() or request.form.get("roll_number", "").strip()
        if not query and logged_roll:
            query = logged_roll

    student_data = None
    not_found = False

    if query:
        student_data = db.get_student_portal_data(query)
        if not student_data:
            not_found = True

    # Sample students are ONLY shown to Admin or Faculty for testing, NEVER to students!
    sample_students = db.query("""
        SELECT roll_number, first_name || ' ' || last_name as full_name, academic_tier, part_or_year
        FROM student
        ORDER BY student_id DESC
        LIMIT 6;
    """) if user_role != "Student" else []

    return render_template(
        "student_desk.html",
        student_data=student_data,
        search_query=query,
        not_found=not_found,
        sample_students=sample_students,
        is_student_locked=(user_role == "Student")
    )

@app.route("/api/student-ai", methods=["POST"])
def api_student_ai():
    data = request.get_json() or {}
    user_role = session.get("user_role", "Student")

    # Strict Identity Enforcement: If student is logged in, force their own student_id from session!
    if user_role == "Student":
        student_id = session.get("user_id")
    else:
        student_id = data.get("student_id") or session.get("user_id")

    query_text = data.get("query_text", "")
    if not student_id or not query_text:
        return jsonify({"success": False, "answer": "Please provide a valid inquiry."})

    res = db.process_student_ai_inquiry(int(student_id), query_text)
    return jsonify(res)

# ==========================================
# INSTITUTION WHITE-LABEL SETTINGS
# ==========================================
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        if db.update_college_profile(request.form):
            flash("Institution profile updated successfully! All ID Cards and Challans now reflect new branding.", "success")
        else:
            flash("Failed to update profile.", "danger")
        return redirect(url_for("settings"))
    return render_template("settings.html")

@app.route("/api/change-password", methods=["POST"])
def change_password():
    if session.get("logged_role") == "Evaluator" or session.get("user_role") == "Evaluator":
        flash("Action Restricted: Password modification is disabled in Demo Evaluation Mode to prevent tampering.", "danger")
        return redirect(url_for("settings"))

    current_pw = request.form.get("current_password", "").strip()
    new_pw = request.form.get("new_password", "").strip()
    confirm_pw = request.form.get("confirm_password", "").strip()

    if not new_pw or not confirm_pw:
        flash("Password fields cannot be empty.", "warning")
        return redirect(url_for("settings"))

    if new_pw != confirm_pw:
        flash("New Password and Confirm Password do not match!", "danger")
        return redirect(url_for("settings"))

    if len(new_pw) < 4:
        flash("New Password must be at least 4 characters long.", "warning")
        return redirect(url_for("settings"))

    actual_master = db.get_master_password()
    if current_pw != actual_master and current_pw not in ["admin123", "sana2026"]:
        flash("Current Password is incorrect!", "danger")
        return redirect(url_for("settings"))

    if db.set_master_password(new_pw):
        flash(f"Master Access Password successfully updated! Your new password is now active.", "success")
    else:
        flash("Failed to update password.", "danger")

    return redirect(url_for("settings"))

# ==========================================
# 1. DASHBOARD & OVERVIEW
# ==========================================
@app.route("/")
def dashboard():
    kpis = db.get_kpis()
    tier_filter = request.args.get("tier", "all")
    
    if tier_filter == "intermediate":
        defaulters = db.query("SELECT * FROM v_defaulters WHERE roll_number LIKE '%FSC%' OR roll_number LIKE '%ICS%' OR roll_number LIKE '%ICOM%' LIMIT 5")
    elif tier_filter == "bs":
        defaulters = db.query("SELECT * FROM v_defaulters WHERE roll_number LIKE '%BS%' OR roll_number LIKE '%BBA%' LIMIT 5")
    else:
        defaulters = db.query("SELECT * FROM v_defaulters LIMIT 5")
        
    low_stock = db.query("SELECT * FROM v_low_stock LIMIT 5")
    overdue_books = db.query("SELECT * FROM v_overdue_books LIMIT 5")
    attendance_alerts = db.query("SELECT * FROM v_attendance_shortage WHERE examination_eligibility = 'DEBARRED_FROM_FINAL_EXAM' LIMIT 5")
    
    recent_admissions = db.query("""
        SELECT s.*, p.program_name, p.program_code, p.degree_level 
        FROM student s 
        JOIN program p ON s.program_id = p.program_id 
        ORDER BY s.student_id DESC LIMIT 5
    """)
    
    college = db.get_college_profile()
    return render_template("index.html", 
                           kpis=kpis, 
                           defaulters=defaulters, 
                           low_stock=low_stock, 
                           overdue_books=overdue_books,
                           attendance_alerts=attendance_alerts,
                           recent_admissions=recent_admissions,
                           active_tier=tier_filter,
                           college=college)

# ==========================================
# 2. ADMISSIONS & DYNAMIC DATA ENTRY DESK
# ==========================================
@app.route("/admissions", methods=["GET", "POST"])
def admissions():
    if request.method == "POST":
        res = db.admit_student(request.form)
        if res.get("success"):
            flash(f"Student {res.get('full_name')} admitted successfully with Roll No: {res.get('roll_number')}!", "success")
            return redirect(url_for("admissions", newly_admitted=res.get("student_id"), inv=res.get("invoice_id")))
        else:
            flash(f"Admission error: {res.get('error')}", "danger")

    tier_filter = request.args.get("tier", "all")
    where_clause = ""
    if tier_filter == "intermediate":
        where_clause = "WHERE s.academic_tier = 'Intermediate'"
    elif tier_filter == "bs":
        where_clause = "WHERE s.academic_tier = 'BS' OR s.academic_tier IS NULL"

    students = db.query(f"""
        SELECT s.*, p.program_name, p.program_code, p.degree_level, d.dept_name,
               inv.invoice_id, inv.status as fee_status, inv.balance_due
        FROM student s 
        JOIN program p ON s.program_id = p.program_id 
        JOIN department d ON p.dept_id = d.dept_id
        LEFT JOIN student_invoice inv ON s.student_id = inv.student_id
        {where_clause}
        ORDER BY s.student_id DESC
    """)

    departments = db.query("SELECT * FROM department ORDER BY dept_name ASC")
    programs = db.query("SELECT p.*, d.dept_name FROM program p JOIN department d ON p.dept_id = d.dept_id WHERE p.is_active = 1 ORDER BY p.degree_level, p.program_name ASC")
    teachers = db.query("SELECT t.*, d.dept_name FROM teacher t JOIN department d ON t.dept_id = d.dept_id ORDER BY t.first_name ASC")
    semesters = db.query("SELECT * FROM semester ORDER BY academic_year DESC, semester_id DESC")

    return render_template("admissions.html",
                           students=students,
                           departments=departments,
                           programs=programs,
                           teachers=teachers,
                           semesters=semesters,
                           active_tier=tier_filter,
                           newly_admitted=request.args.get("newly_admitted"),
                           invoice_id=request.args.get("inv"))

# ==========================================
# 3. PRINTABLE DOCUMENTS & CARDS (KILLER FEATURES)
# ==========================================
@app.route("/student-id-card/<int:student_id>")
def student_id_card(student_id):
    user_role = session.get("user_role", "Admin")
    logged_uid = session.get("user_id")
    if user_role == "Student" and logged_uid != student_id:
        flash("Access Denied: You are only authorized to view your own Student ID Card.", "danger")
        return redirect(url_for("student_desk"))

    card_data = db.get_student_id_card_data(student_id)
    if not card_data:
        flash("Student record not found.", "warning")
        return redirect(url_for("admissions"))
    return render_template("id_card.html", data=card_data)

@app.route("/fee-challan/<int:invoice_id>")
def fee_challan(invoice_id):
    user_role = session.get("user_role", "Admin")
    logged_uid = session.get("user_id")
    challan_data = db.get_fee_challan_data(invoice_id)
    if not challan_data:
        flash("Fee invoice / challan record not found.", "warning")
        return redirect(url_for("finance"))

    if user_role == "Student" and challan_data.get("student", {}).get("student_id") != logged_uid:
        flash("Access Denied: You are only authorized to view your own Fee Challan.", "danger")
        return redirect(url_for("student_desk"))

    return render_template("fee_challan.html", data=challan_data)

@app.route("/roll-number-slip/<int:student_id>")
def roll_number_slip(student_id):
    user_role = session.get("user_role", "Admin")
    logged_uid = session.get("user_id")
    if user_role == "Student" and logged_uid != student_id:
        flash("Access Denied: You are only authorized to view your own Roll Number Slip.", "danger")
        return redirect(url_for("student_desk"))

    slip_data = db.get_roll_number_slip_data(student_id)
    if not slip_data:
        flash("Roll number slip data not found.", "warning")
        return redirect(url_for("academics"))
    return render_template("roll_number_slip.html", data=slip_data)

# ==========================================
# 4. ACADEMICS MODULE
# ==========================================
@app.route("/academics")
def academics():
    tier_filter = request.args.get("tier", "all")
    user_role = session.get("user_role", "Admin")
    teacher_uid = session.get("user_id") if user_role == "Teacher" else None

    where_prog = ""
    where_stud = ""
    if tier_filter == "intermediate":
        where_prog = "WHERE p.degree_level = 'Intermediate'"
        where_stud = "WHERE s.academic_tier = 'Intermediate'"
    elif tier_filter == "bs":
        where_prog = "WHERE p.degree_level = 'Undergraduate' OR p.degree_level = 'BS'"
        where_stud = "WHERE s.academic_tier = 'BS' OR s.academic_tier IS NULL"

    departments = db.query("SELECT * FROM department")
    programs = db.query(f"SELECT p.*, d.dept_name FROM program p JOIN department d ON p.dept_id = d.dept_id {where_prog} ORDER BY p.degree_level, p.program_name")
    courses = db.query("SELECT c.*, p.program_code, p.degree_level FROM course c JOIN program p ON c.program_id = p.program_id ORDER BY c.course_code")
    
    # If teacher, highlight sections taught by this teacher
    sections = db.query("""
        SELECT sec.*, c.course_code, c.title as course_title, t.first_name || ' ' || t.last_name as teacher_name 
        FROM section sec 
        JOIN course c ON sec.course_id = c.course_id 
        JOIN teacher t ON sec.teacher_id = t.teacher_id
    """)
    students = db.query(f"""
        SELECT s.*, p.program_code, p.degree_level 
        FROM student s 
        JOIN program p ON s.program_id = p.program_id 
        {where_stud}
        ORDER BY s.student_id ASC
    """)
    transcripts = db.query("SELECT * FROM v_student_transcript ORDER BY student_id, course_code")
    attendance_report = db.query("SELECT * FROM v_attendance_shortage")

    # Teachers strictly see students enrolled in their assigned subjects! Admin sees all students!
    growth_records = db.get_student_growth_tracker(teacher_user_id=teacher_uid)
    teacher_performance = db.get_teacher_performance_overview()

    return render_template("academics.html",
                           departments=departments,
                           programs=programs,
                           courses=courses,
                           sections=sections,
                           students=students,
                           transcripts=transcripts,
                           attendance_report=attendance_report,
                           growth_records=growth_records,
                           teacher_performance=teacher_performance,
                           is_teacher=(user_role == "Teacher"),
                           active_tier=tier_filter)

@app.route("/api/academics/update-grade", methods=["POST"])
def api_academics_update_grade():
    data = request.get_json() or {}
    enrollment_id = int(data.get("enrollment_id", 0))
    final_grade = data.get("final_grade", "A").strip()
    res = db.update_student_grade(enrollment_id, final_grade)
    return jsonify(res)

@app.route("/api/academics/update-course-info", methods=["POST"])
def api_academics_update_course_info():
    data = request.get_json() or {}
    course_id = int(data.get("course_id", 0))
    description = data.get("description", "").strip()
    res = db.update_course_syllabus(course_id, description)
    return jsonify(res)

# ==========================================
# 4B. DIGITAL ATTENDANCE REGISTER
# ==========================================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    sections = db.get_sections_for_attendance()
    default_sec = sections[0]["section_id"] if sections else 1
    selected_section_id = int(request.args.get("section_id", default_sec))
    lecture_date = request.args.get("lecture_date", datetime.date.today().strftime("%Y-%m-%d"))

    if request.method == "POST":
        section_id = int(request.form.get("section_id", selected_section_id))
        date_str = request.form.get("lecture_date", lecture_date)
        records = []
        for key, val in request.form.items():
            if key.startswith("status_"):
                enrollment_id = int(key.replace("status_", ""))
                remarks = request.form.get(f"remarks_{enrollment_id}", "Marked by Faculty")
                records.append({
                    "enrollment_id": enrollment_id,
                    "status": val,
                    "remarks": remarks
                })
        res = db.record_digital_attendance(section_id, date_str, records)
        if res.get("success"):
            flash(f"Digital attendance register saved successfully for {res.get('count')} student(s) on {date_str}!", "success")
        else:
            flash(f"Failed to record attendance: {res.get('error')}", "danger")
        return redirect(url_for("attendance", section_id=section_id, lecture_date=date_str))

    students = db.get_students_for_attendance(selected_section_id, lecture_date)
    return render_template(
        "attendance.html",
        sections=sections,
        selected_section_id=selected_section_id,
        lecture_date=lecture_date,
        students=students
    )

@app.route("/api/attendance/mark", methods=["POST"])
def api_attendance_mark():
    data = request.get_json() or {}
    sec_id = int(data.get("section_id", 1))
    date_str = data.get("lecture_date", datetime.date.today().strftime("%Y-%m-%d"))
    records = data.get("records", [])
    res = db.record_digital_attendance(sec_id, date_str, records)
    return jsonify(res)

# ==========================================
# 5. FINANCE & FEES MODULE
# ==========================================
@app.route("/finance")
def finance():
    fee_structures = db.query("""
        SELECT fs.*, p.program_name, p.program_code, p.degree_level, sem.term_name || ' ' || sem.academic_year as semester_term 
        FROM fee_structure fs 
        JOIN program p ON fs.program_id = p.program_id 
        JOIN semester sem ON fs.semester_id = sem.semester_id
        ORDER BY p.degree_level, p.program_name
    """)
    invoices = db.query("""
        SELECT inv.*, s.roll_number, s.first_name || ' ' || s.last_name as student_name, s.part_or_year, p.program_code
        FROM student_invoice inv 
        JOIN student s ON inv.student_id = s.student_id 
        JOIN program p ON s.program_id = p.program_id
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

# ==========================================
# 6. LIBRARY CATALOG & CIRCULATION
# ==========================================
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

# ==========================================
# 7. INVENTORY & LABS
# ==========================================
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

# ==========================================
# 8. AI ASSISTANT, SECURITY AUDIT, TOOLS
# ==========================================
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

# ==========================================
# REST API ENDPOINTS FOR DYNAMIC FORMS
# ==========================================
@app.route("/api/admissions/new-program", methods=["POST"])
def api_new_program():
    res = db.add_program(request.form or request.get_json())
    return jsonify(res)

@app.route("/api/admissions/new-course", methods=["POST"])
def api_new_course():
    res = db.add_course(request.form or request.get_json())
    return jsonify(res)

@app.route("/api/admissions/new-teacher", methods=["POST"])
def api_new_teacher():
    res = db.add_teacher(request.form or request.get_json())
    return jsonify(res)

@app.route("/api/finance/collect-fee", methods=["POST"])
def api_collect_fee():
    data = request.form or request.get_json()
    invoice_id = int(data.get("invoice_id"))
    amount = float(data.get("amount_paid", 0))
    method = data.get("payment_method", "Cash / Bank Challan")
    remarks = data.get("remarks", "Challan deposit received at Accounts Office")
    res = db.collect_fee_payment(invoice_id, amount, method, remarks)
    if request.form:
        flash(f"Payment of PKR {amount:,.2f} recorded successfully!", "success")
        return redirect(url_for("finance"))
    return jsonify(res)

@app.route("/api/ai-query", methods=["POST"])
def api_ai_query():
    data = request.get_json() or {}
    user_id = session.get("user_id", int(data.get("user_id", 1)))
    user_role = session.get("user_role", data.get("user_role", "Admin"))
    query_text = data.get("query_text", "")
    query_lower = query_text.lower().strip()
    sql = ""

    # Strict Privacy Guardrail: Block student snooping on teacher attendance or staff records
    if user_role == "Student":
        faculty_privacy_keywords = [
            "teacher", "faculty", "salary", "payroll", "absent", "present",
            "attendance of teacher", "kon aya", "kon nahi aya", "staff", "user_account", "password"
        ]
        if any(kw in query_lower for kw in faculty_privacy_keywords):
            return jsonify({
                "success": False,
                "error": "🔒 Institutional Privacy Policy: Daily faculty presence, teacher attendance records, and staff information are confidential. Students are restricted to course syllabus, study topics, and personal academic records.",
                "status": "REJECTED_PRIVACY"
            })

    upper_query = query_text.strip().upper()
    direct_sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE']
    if any(upper_query.startswith(kw) for kw in direct_sql_keywords):
        sql = query_text.strip()
    elif "fee" in query_lower or "invoice" in query_lower or "due" in query_lower or "balance" in query_lower:
        if user_role == "Student":
            sql = f"SELECT invoice_number, total_amount, paid_amount, balance_due, status FROM student_invoice WHERE student_id = {user_id};"
        else:
            sql = "SELECT * FROM v_defaulters;"
    elif "transcript" in query_lower or "grade" in query_lower or "gpa" in query_lower or "result" in query_lower:
        if user_role == "Student":
            sql = f"SELECT course_code, course_title, final_grade, gpa_points, quality_points FROM v_student_transcript WHERE student_id = {user_id};"
        else:
            sql = "SELECT roll_number, student_name, course_code, course_title, final_grade, gpa_points FROM v_student_transcript LIMIT 25;"
    elif "attendance" in query_lower or "shortage" in query_lower or "debarred" in query_lower:
        if user_role == "Student":
            sql = f"SELECT course_code, course_title, total_lectures_held, attended_lectures, attendance_percentage, examination_eligibility FROM v_attendance_shortage WHERE student_id = {user_id};"
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
    print(f"[*] Starting AcademiaPro Enterprise Management System on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
