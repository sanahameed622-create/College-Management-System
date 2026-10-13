"""
AcademiaPro Database Initializer
Supports direct PostgreSQL initialization as well as local SQLite dual-engine execution.
"""
import os
import sys
import sqlite3

DB_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(os.path.dirname(DB_DIR), "academiapro.db")

def init_sqlite():
    """Initializes a local self-contained SQLite database with full schema and sample data."""
    print(f"[*] Initializing SQLite Database at: {SQLITE_DB_PATH}")
    if os.path.exists(SQLITE_DB_PATH):
        try:
            os.remove(SQLITE_DB_PATH)
            print("[+] Removed existing sqlite database.")
        except Exception as e:
            print(f"[!] Warning removing existing db: {e}")

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. System Core
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS role (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_account (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
    );

    CREATE TABLE IF NOT EXISTS user_role (
        user_id INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE CASCADE,
        role_id INTEGER NOT NULL REFERENCES role(role_id) ON DELETE CASCADE,
        assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, role_id)
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES user_account(user_id) ON DELETE SET NULL,
        action_type TEXT NOT NULL,
        schema_name TEXT NOT NULL,
        table_name TEXT NOT NULL,
        record_id TEXT,
        old_data TEXT,
        new_data TEXT,
        ip_address TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Academics
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS department (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_code TEXT NOT NULL UNIQUE,
        dept_name TEXT NOT NULL UNIQUE,
        office_location TEXT NOT NULL,
        contact_email TEXT NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS program (
        program_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_id INTEGER NOT NULL REFERENCES department(dept_id) ON DELETE RESTRICT,
        program_code TEXT NOT NULL UNIQUE,
        program_name TEXT NOT NULL,
        degree_level TEXT NOT NULL DEFAULT 'Undergraduate',
        total_semesters INTEGER NOT NULL CHECK (total_semesters BETWEEN 1 AND 12),
        total_credits INTEGER NOT NULL CHECK (total_credits BETWEEN 10 AND 200),
        is_active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS semester (
        semester_id INTEGER PRIMARY KEY AUTOINCREMENT,
        term_name TEXT NOT NULL CHECK (term_name IN ('Fall', 'Spring', 'Summer')),
        academic_year INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        is_current INTEGER NOT NULL DEFAULT 0,
        UNIQUE (term_name, academic_year)
    );

    CREATE TABLE IF NOT EXISTS teacher (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_code TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL UNIQUE REFERENCES user_account(user_id) ON DELETE RESTRICT,
        dept_id INTEGER NOT NULL REFERENCES department(dept_id) ON DELETE RESTRICT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        designation TEXT NOT NULL DEFAULT 'Lecturer',
        qualification TEXT NOT NULL,
        hire_date TEXT DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS student (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL UNIQUE REFERENCES user_account(user_id) ON DELETE RESTRICT,
        program_id INTEGER NOT NULL REFERENCES program(program_id) ON DELETE RESTRICT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        cnic TEXT NOT NULL UNIQUE,
        phone TEXT,
        date_of_birth TEXT NOT NULL,
        admission_date TEXT DEFAULT CURRENT_DATE,
        current_semester_num INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Probation', 'Suspended', 'Graduated', 'Withdrawn'))
    );

    CREATE TABLE IF NOT EXISTS course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER NOT NULL REFERENCES program(program_id) ON DELETE RESTRICT,
        course_code TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        credit_hours INTEGER NOT NULL CHECK (credit_hours BETWEEN 1 AND 6),
        is_lab_required INTEGER NOT NULL DEFAULT 0,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS section (
        section_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE RESTRICT,
        semester_id INTEGER NOT NULL REFERENCES semester(semester_id) ON DELETE RESTRICT,
        teacher_id INTEGER NOT NULL REFERENCES teacher(teacher_id) ON DELETE RESTRICT,
        section_name TEXT NOT NULL,
        max_capacity INTEGER NOT NULL DEFAULT 40,
        enrolled_count INTEGER NOT NULL DEFAULT 0,
        room_number TEXT NOT NULL,
        UNIQUE (course_id, semester_id, section_name)
    );

    CREATE TABLE IF NOT EXISTS enrollment (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
        section_id INTEGER NOT NULL REFERENCES section(section_id) ON DELETE RESTRICT,
        enrollment_date TEXT DEFAULT CURRENT_DATE,
        status TEXT NOT NULL DEFAULT 'Enrolled' CHECK (status IN ('Enrolled', 'Completed', 'Dropped', 'Withdrawn')),
        final_grade TEXT,
        gpa_points REAL,
        UNIQUE (student_id, section_id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER NOT NULL REFERENCES enrollment(enrollment_id) ON DELETE CASCADE,
        lecture_date TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
        remarks TEXT,
        marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (enrollment_id, lecture_date)
    );

    CREATE TABLE IF NOT EXISTS assessment (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_id INTEGER NOT NULL REFERENCES section(section_id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        assessment_type TEXT NOT NULL CHECK (assessment_type IN ('Quiz', 'Assignment', 'Midterm', 'Final', 'Project', 'Lab_Viva')),
        max_marks REAL NOT NULL CHECK (max_marks > 0),
        weightage_percent REAL NOT NULL CHECK (weightage_percent BETWEEN 1 AND 100),
        due_date TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS assessment_result (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL REFERENCES assessment(assessment_id) ON DELETE CASCADE,
        enrollment_id INTEGER NOT NULL REFERENCES enrollment(enrollment_id) ON DELETE CASCADE,
        marks_obtained REAL NOT NULL CHECK (marks_obtained >= 0),
        remarks TEXT,
        graded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (assessment_id, enrollment_id)
    );
    """)

    # 3. Finance
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS fee_structure (
        fee_structure_id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER NOT NULL REFERENCES program(program_id) ON DELETE RESTRICT,
        semester_id INTEGER NOT NULL REFERENCES semester(semester_id) ON DELETE RESTRICT,
        tuition_fee REAL NOT NULL,
        lab_fee REAL NOT NULL DEFAULT 0,
        library_fund REAL NOT NULL DEFAULT 0,
        exam_fee REAL NOT NULL DEFAULT 0,
        total_structure_amount REAL NOT NULL,
        UNIQUE (program_id, semester_id)
    );

    CREATE TABLE IF NOT EXISTS student_invoice (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT NOT NULL UNIQUE,
        student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE RESTRICT,
        semester_id INTEGER NOT NULL REFERENCES semester(semester_id) ON DELETE RESTRICT,
        fee_structure_id INTEGER NOT NULL REFERENCES fee_structure(fee_structure_id) ON DELETE RESTRICT,
        total_amount REAL NOT NULL,
        paid_amount REAL NOT NULL DEFAULT 0.0,
        balance_due REAL NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Unpaid' CHECK (status IN ('Unpaid', 'Partial', 'Paid', 'Cancelled')),
        UNIQUE (student_id, semester_id)
    );

    CREATE TABLE IF NOT EXISTS fee_payment (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL REFERENCES student_invoice(invoice_id) ON DELETE RESTRICT,
        payment_reference TEXT NOT NULL UNIQUE,
        amount_paid REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        received_by_user_id INTEGER REFERENCES user_account(user_id) ON DELETE SET NULL,
        remarks TEXT
    );

    CREATE TABLE IF NOT EXISTS fine (
        fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE RESTRICT,
        fine_type TEXT NOT NULL,
        amount REAL NOT NULL,
        reason TEXT NOT NULL,
        source_reference_id TEXT,
        is_paid INTEGER NOT NULL DEFAULT 0,
        paid_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Library
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS book (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        publisher TEXT,
        publication_year INTEGER,
        category TEXT NOT NULL DEFAULT 'General'
    );

    CREATE TABLE IF NOT EXISTS book_copy (
        copy_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE RESTRICT,
        barcode TEXT NOT NULL UNIQUE,
        edition TEXT DEFAULT '1st Edition',
        shelf_location TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available'
    );

    CREATE TABLE IF NOT EXISTS library_member (
        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE REFERENCES user_account(user_id) ON DELETE RESTRICT,
        membership_number TEXT NOT NULL UNIQUE,
        member_type TEXT NOT NULL,
        max_allowed_books INTEGER NOT NULL DEFAULT 3,
        is_active INTEGER NOT NULL DEFAULT 1,
        joined_date TEXT DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS book_issue (
        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        copy_id INTEGER NOT NULL REFERENCES book_copy(copy_id) ON DELETE RESTRICT,
        member_id INTEGER NOT NULL REFERENCES library_member(member_id) ON DELETE RESTRICT,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        return_date TEXT,
        overdue_fine REAL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'Issued'
    );
    """)

    # 5. Inventory
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS item_category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS room_lab (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_id INTEGER NOT NULL REFERENCES department(dept_id) ON DELETE RESTRICT,
        room_number TEXT NOT NULL,
        room_name TEXT,
        room_type TEXT NOT NULL,
        capacity INTEGER NOT NULL DEFAULT 30,
        UNIQUE (dept_id, room_number)
    );

    CREATE TABLE IF NOT EXISTS inventory_item (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL REFERENCES item_category(category_id) ON DELETE RESTRICT,
        item_code TEXT NOT NULL UNIQUE,
        item_name TEXT NOT NULL,
        unit_of_measure TEXT NOT NULL DEFAULT 'Units',
        total_stock INTEGER NOT NULL DEFAULT 0,
        available_stock INTEGER NOT NULL DEFAULT 0,
        min_reorder_level INTEGER NOT NULL DEFAULT 5
    );

    CREATE TABLE IF NOT EXISTS purchase_order (
        po_id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_number TEXT NOT NULL UNIQUE,
        vendor_name TEXT NOT NULL,
        order_date TEXT DEFAULT CURRENT_DATE,
        total_cost REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'Pending',
        ordered_by_user_id INTEGER REFERENCES user_account(user_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS purchase_item (
        po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id INTEGER NOT NULL REFERENCES purchase_order(po_id) ON DELETE CASCADE,
        item_id INTEGER NOT NULL REFERENCES inventory_item(item_id) ON DELETE RESTRICT,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        line_total REAL NOT NULL,
        UNIQUE (po_id, item_id)
    );

    CREATE TABLE IF NOT EXISTS item_issuance (
        issuance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL REFERENCES inventory_item(item_id) ON DELETE RESTRICT,
        room_id INTEGER NOT NULL REFERENCES room_lab(room_id) ON DELETE RESTRICT,
        issued_to_user_id INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE RESTRICT,
        quantity INTEGER NOT NULL,
        issue_date TEXT DEFAULT CURRENT_DATE,
        return_date TEXT,
        condition_notes TEXT,
        status TEXT NOT NULL DEFAULT 'In_Use'
    );
    """)

    # 6. AI Schema
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS conversation (
        conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE CASCADE,
        session_title TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS message (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL REFERENCES conversation(conversation_id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE RESTRICT,
        user_role TEXT NOT NULL,
        user_query TEXT NOT NULL,
        generated_sql TEXT,
        execution_status TEXT NOT NULL DEFAULT 'SUCCESS',
        row_count_returned INTEGER DEFAULT 0,
        response_summary TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Views
    cursor.executescript("""
    CREATE VIEW IF NOT EXISTS v_student_transcript AS
    SELECT 
        s.student_id,
        s.roll_number,
        s.first_name || ' ' || s.last_name AS student_name,
        p.program_code,
        p.program_name,
        sem.term_name || ' ' || sem.academic_year AS semester_term,
        c.course_code,
        c.title AS course_title,
        c.credit_hours,
        sec.section_name,
        e.status AS enrollment_status,
        e.final_grade,
        e.gpa_points,
        ROUND((c.credit_hours * COALESCE(e.gpa_points, 0.00)), 2) AS quality_points
    FROM student s
    JOIN program p ON s.program_id = p.program_id
    JOIN enrollment e ON s.student_id = e.student_id
    JOIN section sec ON e.section_id = sec.section_id
    JOIN course c ON sec.course_id = c.course_id
    JOIN semester sem ON sec.semester_id = sem.semester_id;

    CREATE VIEW IF NOT EXISTS v_defaulters AS
    SELECT 
        s.student_id,
        s.roll_number,
        s.first_name || ' ' || s.last_name AS student_name,
        s.email,
        p.program_code,
        inv.invoice_number,
        sem.term_name || ' ' || sem.academic_year AS semester_term,
        inv.total_amount,
        inv.paid_amount,
        inv.balance_due AS invoice_balance_due,
        inv.due_date,
        COALESCE(fn.total_unpaid_fines, 0.00) AS unpaid_fines,
        (inv.balance_due + COALESCE(fn.total_unpaid_fines, 0.00)) AS total_outstanding_liability,
        CASE 
            WHEN date('now') > inv.due_date THEN 'Overdue Defaulter'
            ELSE 'Pending Payment'
        END AS defaulter_status
    FROM student_invoice inv
    JOIN student s ON inv.student_id = s.student_id
    JOIN program p ON s.program_id = p.program_id
    JOIN semester sem ON inv.semester_id = sem.semester_id
    LEFT JOIN (
        SELECT student_id, SUM(amount) AS total_unpaid_fines
        FROM fine
        WHERE is_paid = 0
        GROUP BY student_id
    ) fn ON s.student_id = fn.student_id
    WHERE inv.balance_due > 0;

    CREATE VIEW IF NOT EXISTS v_low_stock AS
    SELECT 
        itm.item_id,
        itm.item_code,
        itm.item_name,
        cat.category_name,
        itm.unit_of_measure,
        itm.total_stock,
        itm.available_stock,
        itm.min_reorder_level,
        (itm.min_reorder_level - itm.available_stock) AS reorder_shortage_quantity,
        'Central Store / Labs' AS deployed_locations
    FROM inventory_item itm
    JOIN item_category cat ON itm.category_id = cat.category_id
    WHERE itm.available_stock <= itm.min_reorder_level;

    CREATE VIEW IF NOT EXISTS v_overdue_books AS
    SELECT 
        bi.issue_id,
        b.title AS book_title,
        b.isbn,
        bc.barcode,
        lm.membership_number,
        ua.full_name AS borrower_name,
        ua.email AS borrower_email,
        lm.member_type,
        bi.issue_date,
        bi.due_date,
        ROUND((julianday('now') - julianday(bi.due_date)), 0) AS days_overdue,
        ROUND(((julianday('now') - julianday(bi.due_date)) * 10.00), 2) AS calculated_fine
    FROM book_issue bi
    JOIN book_copy bc ON bi.copy_id = bc.copy_id
    JOIN book b ON bc.book_id = b.book_id
    JOIN library_member lm ON bi.member_id = lm.member_id
    JOIN user_account ua ON lm.user_id = ua.user_id
    WHERE bi.status = 'Issued' AND date('now') > bi.due_date;

    CREATE VIEW IF NOT EXISTS v_attendance_shortage AS
    SELECT 
        s.student_id,
        s.roll_number,
        s.first_name || ' ' || s.last_name AS student_name,
        c.course_code,
        c.title AS course_title,
        sec.section_name,
        COUNT(a.attendance_id) AS total_lectures_held,
        COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END) AS attended_lectures,
        ROUND(
            (CAST(COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END) AS REAL) / 
             NULLIF(COUNT(a.attendance_id), 0)) * 100.0, 2
        ) AS attendance_percentage,
        CASE 
            WHEN (CAST(COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END) AS REAL) / NULLIF(COUNT(a.attendance_id), 0)) * 100.0 < 75.0
            THEN 'DEBARRED_FROM_FINAL_EXAM'
            ELSE 'ELIGIBLE'
        END AS examination_eligibility
    FROM student s
    JOIN enrollment e ON s.student_id = e.student_id
    JOIN section sec ON e.section_id = sec.section_id
    JOIN course c ON sec.course_id = c.course_id
    LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
    GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, c.course_code, c.title, sec.section_name;
    """)

    # Populate Sample Data
    cursor.executescript("""
    INSERT OR IGNORE INTO role (role_id, role_name, description) VALUES
    (1, 'Admin', 'System Administrator with full superuser privileges'),
    (2, 'Teacher', 'Academic faculty member with grading and attendance rights'),
    (3, 'Student', 'Enrolled student with view access to transcripts, fee, library'),
    (4, 'Accountant', 'Finance officer managing fee invoices, payments, and fines'),
    (5, 'Librarian', 'Library manager handling books catalog and circulation'),
    (6, 'StoreKeeper', 'Inventory manager tracking equipment, stock, and room issuances'),
    (7, 'AI_Agent', 'Read-only automated assistant role querying analytical views');

    INSERT OR IGNORE INTO user_account (user_id, username, email, password_hash, full_name) VALUES
    (1, 'admin', 'admin@academiapro.edu.pk', 'pbkdf2:sha256:admin123', 'Engr. Shahbaz Ahmed'),
    (2, 'prof_tariq', 'tariq.mahmood@academiapro.edu.pk', 'pbkdf2:sha256:tariq123', 'Dr. Tariq Mahmood'),
    (3, 'prof_sarah', 'sarah.khan@academiapro.edu.pk', 'pbkdf2:sha256:sarah123', 'Dr. Sarah Khan'),
    (4, 'lect_usman', 'usman.ali@academiapro.edu.pk', 'pbkdf2:sha256:usman123', 'Lect. Usman Ali'),
    (5, 'prof_farooq', 'farooq.azam@academiapro.edu.pk', 'pbkdf2:sha256:farooq123', 'Prof. Farooq Azam'),
    (6, 'accountant_bilal', 'accounts@academiapro.edu.pk', 'pbkdf2:sha256:acc123', 'Bilal Saeed (Accountant)'),
    (7, 'librarian_ayesha', 'library@academiapro.edu.pk', 'pbkdf2:sha256:lib123', 'Ayesha Siddiqua (Librarian)'),
    (8, 'store_imran', 'inventory@academiapro.edu.pk', 'pbkdf2:sha256:store123', 'Imran Rafiq (Store Keeper)'),
    (9, 'ai_system', 'ai.bot@academiapro.edu.pk', 'pbkdf2:sha256:aibot123', 'AcademiaPro AI Assistant'),
    (10, 'std_ali_khan', 'ali.khan@student.edu.pk', 'pbkdf2:sha256:std123', 'Ali Khan'),
    (11, 'std_bilal_ahmed', 'bilal.ahmed@student.edu.pk', 'pbkdf2:sha256:std123', 'Bilal Ahmed'),
    (12, 'std_fatima_zahra', 'fatima.zahra@student.edu.pk', 'pbkdf2:sha256:std123', 'Fatima Zahra'),
    (13, 'std_hamza_tariq', 'hamza.tariq@student.edu.pk', 'pbkdf2:sha256:std123', 'Hamza Tariq'),
    (14, 'std_zainab_bibi', 'zainab.bibi@student.edu.pk', 'pbkdf2:sha256:std123', 'Zainab Bibi'),
    (15, 'std_omar_farooq', 'omar.farooq@student.edu.pk', 'pbkdf2:sha256:std123', 'Omar Farooq'),
    (16, 'std_hassan_raza', 'hassan.raza@student.edu.pk', 'pbkdf2:sha256:std123', 'Hassan Raza'),
    (17, 'std_maryam_noor', 'maryam.noor@student.edu.pk', 'pbkdf2:sha256:std123', 'Maryam Noor'),
    (18, 'std_daniyal_mir', 'daniyal.mir@student.edu.pk', 'pbkdf2:sha256:std123', 'Daniyal Mir'),
    (19, 'std_anaya_malik', 'anaya.malik@student.edu.pk', 'pbkdf2:sha256:std123', 'Anaya Malik'),
    (20, 'std_saad_iqbal', 'saad.iqbal@student.edu.pk', 'pbkdf2:sha256:std123', 'Saad Iqbal');

    INSERT OR IGNORE INTO user_role (user_id, role_id) VALUES
    (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 4), (7, 5), (8, 6), (9, 7),
    (10, 3), (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3), (17, 3), (18, 3), (19, 3), (20, 3);

    INSERT OR IGNORE INTO department (dept_id, dept_code, dept_name, office_location, contact_email) VALUES
    (1, 'CS', 'Department of Computer Science', 'Block A, 2nd Floor', 'cs@academiapro.edu.pk'),
    (2, 'SE', 'Department of Software Engineering', 'Block A, 3rd Floor', 'se@academiapro.edu.pk'),
    (3, 'EE', 'Department of Electrical Engineering', 'Block B, 1st Floor', 'ee@academiapro.edu.pk'),
    (4, 'MS', 'Department of Management Sciences', 'Block C, Ground Floor', 'ms@academiapro.edu.pk');

    INSERT OR IGNORE INTO program (program_id, dept_id, program_code, program_name, degree_level, total_semesters, total_credits) VALUES
    (1, 1, 'BSCS', 'Bachelor of Science in Computer Science', 'Undergraduate', 8, 134),
    (2, 2, 'BSSE', 'Bachelor of Science in Software Engineering', 'Undergraduate', 8, 136),
    (3, 1, 'BSAI', 'Bachelor of Science in Artificial Intelligence', 'Undergraduate', 8, 130),
    (4, 4, 'BBA', 'Bachelor of Business Administration', 'Undergraduate', 8, 132);

    INSERT OR IGNORE INTO semester (semester_id, term_name, academic_year, start_date, end_date, is_current) VALUES
    (1, 'Fall', 2025, '2025-09-01', '2026-01-20', 0),
    (2, 'Spring', 2026, '2026-02-01', '2026-06-25', 1),
    (3, 'Fall', 2026, '2026-09-01', '2027-01-20', 0);

    INSERT OR IGNORE INTO teacher (teacher_id, employee_code, user_id, dept_id, first_name, last_name, email, phone, designation, qualification) VALUES
    (1, 'EMP-101', 2, 1, 'Tariq', 'Mahmood', 'tariq.mahmood@academiapro.edu.pk', '0300-1234567', 'Professor', 'PhD Computer Science'),
    (2, 'EMP-102', 3, 1, 'Sarah', 'Khan', 'sarah.khan@academiapro.edu.pk', '0300-2345678', 'Associate Professor', 'PhD Software Engineering'),
    (3, 'EMP-103', 4, 2, 'Usman', 'Ali', 'usman.ali@academiapro.edu.pk', '0300-3456789', 'Lecturer', 'MS Computer Science'),
    (4, 'EMP-104', 5, 4, 'Farooq', 'Azam', 'farooq.azam@academiapro.edu.pk', '0300-4567890', 'Professor', 'PhD Finance');

    INSERT OR IGNORE INTO student (student_id, roll_number, user_id, program_id, first_name, last_name, email, cnic, phone, date_of_birth, admission_date, current_semester_num, status) VALUES
    (1, 'BSCS-22-01', 10, 1, 'Ali', 'Khan', 'ali.khan@student.edu.pk', '35201-1111111-1', '0321-1000001', '2004-03-15', '2022-09-10', 4, 'Active'),
    (2, 'BSCS-22-02', 11, 1, 'Bilal', 'Ahmed', 'bilal.ahmed@student.edu.pk', '35201-2222222-2', '0321-2000002', '2004-06-20', '2022-09-10', 4, 'Active'),
    (3, 'BSCS-22-03', 12, 1, 'Fatima', 'Zahra', 'fatima.zahra@student.edu.pk', '35201-3333333-3', '0321-3000003', '2005-01-10', '2022-09-10', 4, 'Active'),
    (4, 'BSSE-22-01', 13, 2, 'Hamza', 'Tariq', 'hamza.tariq@student.edu.pk', '35201-4444444-4', '0321-4000004', '2003-11-25', '2022-09-10', 4, 'Active'),
    (5, 'BSSE-22-02', 14, 2, 'Zainab', 'Bibi', 'zainab.bibi@student.edu.pk', '35201-5555555-5', '0321-5000005', '2004-08-14', '2022-09-10', 4, 'Active'),
    (6, 'BSAI-23-01', 15, 3, 'Omar', 'Farooq', 'omar.farooq@student.edu.pk', '35201-6666666-6', '0321-6000006', '2005-04-12', '2023-09-12', 2, 'Active'),
    (7, 'BSAI-23-02', 16, 3, 'Hassan', 'Raza', 'hassan.raza@student.edu.pk', '35201-7777777-7', '0321-7000007', '2005-07-07', '2023-09-12', 2, 'Active'),
    (8, 'BBA-22-01', 17, 4, 'Maryam', 'Noor', 'maryam.noor@student.edu.pk', '35201-8888888-8', '0321-8000008', '2004-02-18', '2022-09-10', 4, 'Active'),
    (9, 'BBA-22-02', 18, 4, 'Daniyal', 'Mir', 'daniyal.mir@student.edu.pk', '35201-9999999-9', '0321-9000009', '2004-09-30', '2022-09-10', 4, 'Probation'),
    (10, 'BSCS-22-04', 19, 1, 'Anaya', 'Malik', 'anaya.malik@student.edu.pk', '35201-1010101-0', '0321-1010101', '2005-05-05', '2022-09-10', 4, 'Active'),
    (11, 'BSCS-22-05', 20, 1, 'Saad', 'Iqbal', 'saad.iqbal@student.edu.pk', '35201-2020202-0', '0321-2020202', '2004-12-12', '2022-09-10', 4, 'Active');

    INSERT OR IGNORE INTO course (course_id, program_id, course_code, title, credit_hours, is_lab_required, description) VALUES
    (1, 1, 'CS-201', 'Database Systems', 4, 1, 'Relational model, SQL, normalization, concurrency and transactions.'),
    (2, 1, 'CS-202', 'Data Structures & Algorithms', 4, 1, 'Arrays, stacks, queues, trees, graphs, sorting and searching.'),
    (3, 1, 'CS-301', 'Operating Systems', 4, 1, 'Processes, threads, memory management, scheduling, file systems.'),
    (4, 2, 'SE-201', 'Software Engineering Principles', 3, 0, 'Software lifecycles, Agile, requirements engineering, UML.'),
    (5, 2, 'SE-202', 'Software Architecture & Design', 3, 0, 'Design patterns, microservices, architectural styles.'),
    (6, 3, 'AI-101', 'Introduction to Artificial Intelligence', 3, 1, 'State space search, knowledge representation, introductory ML.'),
    (7, 4, 'MG-101', 'Principles of Management', 3, 0, 'Organizational behavior, planning, leadership and control.'),
    (8, 4, 'FN-201', 'Financial Accounting', 3, 0, 'Balance sheets, ledger accounts, cash flow statements.');

    INSERT OR IGNORE INTO section (section_id, course_id, semester_id, teacher_id, section_name, max_capacity, enrolled_count, room_number) VALUES
    (1, 1, 2, 1, 'A', 40, 5, 'Block A - Hall 1'),
    (2, 1, 2, 2, 'B', 35, 3, 'Block A - Hall 2'),
    (3, 2, 2, 1, 'A', 40, 4, 'Block A - Lab 1'),
    (4, 3, 2, 3, 'A', 35, 3, 'Block A - Lab 2'),
    (5, 4, 2, 2, 'A', 40, 2, 'Block A - Hall 3'),
    (6, 7, 2, 4, 'A', 45, 2, 'Block C - Hall 1');

    INSERT OR IGNORE INTO enrollment (enrollment_id, student_id, section_id, enrollment_date, status, final_grade, gpa_points) VALUES
    (1, 1, 1, '2026-02-05', 'Enrolled', 'A', 4.00),
    (2, 2, 1, '2026-02-05', 'Enrolled', 'B+', 3.33),
    (3, 3, 1, '2026-02-05', 'Enrolled', 'A', 4.00),
    (4, 10, 1, '2026-02-05', 'Enrolled', 'C', 2.00),
    (5, 11, 1, '2026-02-05', 'Enrolled', 'F', 0.00),
    (6, 1, 3, '2026-02-05', 'Enrolled', 'A', 4.00),
    (7, 2, 3, '2026-02-05', 'Enrolled', 'B', 3.00),
    (8, 3, 3, '2026-02-05', 'Enrolled', 'B+', 3.33),
    (9, 10, 3, '2026-02-05', 'Enrolled', 'B', 3.00),
    (10, 4, 5, '2026-02-05', 'Enrolled', 'A', 4.00),
    (11, 5, 5, '2026-02-05', 'Enrolled', 'B+', 3.33),
    (12, 8, 6, '2026-02-05', 'Enrolled', 'A', 4.00),
    (13, 9, 6, '2026-02-05', 'Enrolled', 'C+', 2.33),
    (14, 1, 4, '2026-02-05', 'Enrolled', 'A', 4.00),
    (15, 2, 4, '2026-02-05', 'Enrolled', 'B', 3.00),
    (16, 3, 4, '2026-02-05', 'Enrolled', 'A', 4.00);

    INSERT OR IGNORE INTO attendance (attendance_id, enrollment_id, lecture_date, status, remarks) VALUES
    (1, 1, '2026-02-10', 'Present', 'On time'),
    (2, 1, '2026-02-12', 'Present', 'Active participant'),
    (3, 1, '2026-02-17', 'Present', 'On time'),
    (4, 1, '2026-02-19', 'Present', 'On time'),
    (5, 5, '2026-02-10', 'Absent', 'Unexcused absence'),
    (6, 5, '2026-02-12', 'Absent', 'Unexcused absence'),
    (7, 5, '2026-02-17', 'Present', 'Late arrival'),
    (8, 5, '2026-02-19', 'Absent', 'Medical leave submitted');

    INSERT OR IGNORE INTO fee_structure (fee_structure_id, program_id, semester_id, tuition_fee, lab_fee, library_fund, exam_fee, total_structure_amount) VALUES
    (1, 1, 2, 75000.0, 10000.0, 3000.0, 4000.0, 92000.0),
    (2, 2, 2, 78000.0, 10000.0, 3000.0, 4000.0, 95000.0),
    (3, 3, 2, 80000.0, 12000.0, 3000.0, 4000.0, 99000.0),
    (4, 4, 2, 70000.0, 3000.0,  3000.0, 4000.0, 80000.0);

    INSERT OR IGNORE INTO student_invoice (invoice_id, invoice_number, student_id, semester_id, fee_structure_id, total_amount, paid_amount, balance_due, issue_date, due_date, status) VALUES
    (1, 'INV-2026-00001', 1, 2, 1, 92000.0, 92000.0, 0.0,     '2026-02-01', '2026-02-20', 'Paid'),
    (2, 'INV-2026-00002', 2, 2, 1, 92000.0, 50000.0, 42000.0, '2026-02-01', '2026-02-20', 'Partial'),
    (3, 'INV-2026-00003', 3, 2, 1, 92000.0, 92000.0, 0.0,     '2026-02-01', '2026-02-20', 'Paid'),
    (4, 'INV-2026-00004', 4, 2, 2, 95000.0, 0.0,     95000.0, '2026-02-01', '2026-02-20', 'Unpaid'),
    (5, 'INV-2026-00005', 9, 2, 4, 80000.0, 0.0,     80000.0, '2026-02-01', '2026-02-20', 'Unpaid');

    INSERT OR IGNORE INTO fine (fine_id, student_id, fine_type, amount, reason, source_reference_id, is_paid) VALUES
    (1, 2, 'Library_Overdue', 350.0, 'Overdue book copy BK-101-C1 returned 35 days late', 'ISSUE-101', 0),
    (2, 9, 'Discipline',      1500.0, 'Unauthorized vehicle parking in faculty lane', 'DISC-091', 0);

    INSERT OR IGNORE INTO book (book_id, isbn, title, author, publisher, publication_year, category) VALUES
    (1, '978-0133970777', 'Database System Concepts', 'Abraham Silberschatz', 'McGraw-Hill', 2020, 'Computer Science'),
    (2, '978-0262033848', 'Introduction to Algorithms (CLRS)', 'Thomas H. Cormen', 'MIT Press', 2022, 'Computer Science'),
    (3, '978-0133591620', 'Modern Operating Systems', 'Andrew S. Tanenbaum', 'Pearson', 2015, 'Computer Science'),
    (4, '978-0134757599', 'Software Engineering: A Practitioner Approach', 'Roger S. Pressman', 'McGraw-Hill', 2020, 'Software Engineering');

    INSERT OR IGNORE INTO book_copy (copy_id, book_id, barcode, edition, shelf_location, status) VALUES
    (1, 1, 'BC-DB-001', '7th Edition', 'Shelf CS-01', 'Available'),
    (2, 1, 'BC-DB-002', '7th Edition', 'Shelf CS-01', 'Issued'),
    (3, 2, 'BC-AL-001', '4th Edition', 'Shelf CS-02', 'Available'),
    (4, 2, 'BC-AL-002', '4th Edition', 'Shelf CS-02', 'Issued');

    INSERT OR IGNORE INTO library_member (member_id, user_id, membership_number, member_type, max_allowed_books) VALUES
    (1, 10, 'LIB-STD-001', 'Student', 3),
    (2, 11, 'LIB-STD-002', 'Student', 3),
    (3, 2,  'LIB-FAC-001', 'Faculty', 5);

    INSERT OR IGNORE INTO book_issue (issue_id, copy_id, member_id, issue_date, due_date, return_date, overdue_fine, status) VALUES
    (1, 2, 1, '2026-02-10', '2026-02-24', '2026-02-22', 0.0, 'Returned'),
    (2, 4, 2, '2026-01-10', '2026-01-24', NULL, 0.0, 'Issued');

    INSERT OR IGNORE INTO item_category (category_id, category_name, description) VALUES
    (1, 'Lab Equipment', 'Specialized test, electronics and measurement devices for engineering labs'),
    (2, 'IT Hardware', 'Workstations, servers, switches, routers and projectors'),
    (3, 'Classroom Furniture', 'Lecture desks, ergonomic teacher chairs, whiteboards'),
    (4, 'Stationery', 'Board markers, printer reams, registers, examination paper');

    INSERT OR IGNORE INTO room_lab (room_id, dept_id, room_number, room_name, room_type, capacity) VALUES
    (1, 1, 'Lab-A1', 'Software Development Lab', 'Computer_Lab', 45),
    (2, 1, 'Lab-A2', 'AI & Deep Learning GPU Lab', 'Computer_Lab', 30),
    (3, 3, 'Lab-B1', 'Circuits & Embedded Systems Lab', 'Physics_Lab', 35);

    INSERT OR IGNORE INTO inventory_item (item_id, category_id, item_code, item_name, unit_of_measure, total_stock, available_stock, min_reorder_level) VALUES
    (1, 2, 'IT-PC-DELL-5820', 'Dell Precision 5820 Workstation', 'Units', 50, 4, 10),
    (2, 2, 'IT-SW-CISCO-2960', 'Cisco Catalyst 24-Port Gigabit Switch', 'Units', 8, 2, 3),
    (3, 2, 'IT-PRJ-EPSON-4K', 'Epson EB-2250U Ceiling Projector', 'Units', 12, 8, 4),
    (4, 3, 'FN-CHAIR-STUDENT', 'Heavy Duty Student Desk Chair', 'Units', 200, 180, 25);

    INSERT OR IGNORE INTO conversation (conversation_id, user_id, session_title) VALUES
    (1, 10, 'Student Ali Khan - Fee & Grades Inquiry'),
    (2, 1,  'Admin Shahbaz - Department Defaulters Query');

    INSERT OR IGNORE INTO message (message_id, conversation_id, user_id, user_role, user_query, generated_sql, execution_status, row_count_returned, response_summary) VALUES
    (1, 1, 10, 'Student', 'What is my current semester fee status?', 
     'SELECT invoice_number, total_amount, paid_amount, balance_due, status FROM student_invoice WHERE student_id = 1;', 
     'SUCCESS', 1, 'Invoice INV-2026-00001 is Paid in Full. Balance due is Rs. 0.00.'),
    (2, 2, 1, 'Admin', 'Show me all students who have not cleared their fee.',
     'SELECT roll_number, student_name, total_outstanding_liability FROM v_defaulters;',
     'SUCCESS', 3, 'Found 3 fee defaulters with total outstanding liability across campus.');
    """)

    conn.commit()
    conn.close()
    print("[+] SQLite database successfully initialized with all tables, views, and sample data!")

if __name__ == "__main__":
    init_sqlite()
