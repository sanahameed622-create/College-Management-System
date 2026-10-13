-- ============================================================================
-- AcademiaPro - Integrated College Management System
-- Module: 01_schema_ddl.sql
-- Description: Complete PostgreSQL 16+ DDL with 6 schemas, robust constraints,
--              PK/FK/UNIQUE/CHECK, and index optimization.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS system_core;
CREATE SCHEMA IF NOT EXISTS academics;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS library;
CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS ai;

-- 1. SYSTEM_CORE SCHEMA
CREATE TABLE IF NOT EXISTS system_core.role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_core.user_account (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_email_format CHECK (email LIKE '%_@__%.__%')
);

CREATE TABLE IF NOT EXISTS system_core.user_role (
    user_id INT NOT NULL REFERENCES system_core.user_account(user_id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES system_core.role(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS system_core.audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    user_id INT REFERENCES system_core.user_account(user_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    schema_name VARCHAR(50) NOT NULL,
    table_name VARCHAR(80) NOT NULL,
    record_id VARCHAR(50),
    old_data JSONB,
    new_data JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. ACADEMICS SCHEMA
CREATE TABLE IF NOT EXISTS academics.department (
    dept_id SERIAL PRIMARY KEY,
    dept_code VARCHAR(15) NOT NULL UNIQUE,
    dept_name VARCHAR(120) NOT NULL UNIQUE,
    office_location VARCHAR(100) NOT NULL,
    contact_email VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS academics.program (
    program_id SERIAL PRIMARY KEY,
    dept_id INT NOT NULL REFERENCES academics.department(dept_id) ON DELETE RESTRICT,
    program_code VARCHAR(20) NOT NULL UNIQUE,
    program_name VARCHAR(150) NOT NULL,
    degree_level VARCHAR(30) NOT NULL DEFAULT 'Undergraduate',
    total_semesters INT NOT NULL CHECK (total_semesters BETWEEN 1 AND 12),
    total_credits INT NOT NULL CHECK (total_credits BETWEEN 10 AND 200),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS academics.semester (
    semester_id SERIAL PRIMARY KEY,
    term_name VARCHAR(20) NOT NULL CHECK (term_name IN ('Fall', 'Spring', 'Summer')),
    academic_year INT NOT NULL CHECK (academic_year BETWEEN 2000 AND 2100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_semester_dates CHECK (end_date > start_date),
    CONSTRAINT uq_semester_term_year UNIQUE (term_name, academic_year)
);

CREATE TABLE IF NOT EXISTS academics.teacher (
    teacher_id SERIAL PRIMARY KEY,
    employee_code VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL UNIQUE REFERENCES system_core.user_account(user_id) ON DELETE RESTRICT,
    dept_id INT NOT NULL REFERENCES academics.department(dept_id) ON DELETE RESTRICT,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30),
    designation VARCHAR(60) NOT NULL DEFAULT 'Lecturer',
    qualification VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS academics.student (
    student_id SERIAL PRIMARY KEY,
    roll_number VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL UNIQUE REFERENCES system_core.user_account(user_id) ON DELETE RESTRICT,
    program_id INT NOT NULL REFERENCES academics.program(program_id) ON DELETE RESTRICT,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    cnic VARCHAR(25) NOT NULL UNIQUE,
    phone VARCHAR(30),
    date_of_birth DATE NOT NULL,
    admission_date DATE NOT NULL DEFAULT CURRENT_DATE,
    current_semester_num INT NOT NULL DEFAULT 1 CHECK (current_semester_num BETWEEN 1 AND 12),
    status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Probation', 'Suspended', 'Graduated', 'Withdrawn'))
);

CREATE TABLE IF NOT EXISTS academics.course (
    course_id SERIAL PRIMARY KEY,
    program_id INT NOT NULL REFERENCES academics.program(program_id) ON DELETE RESTRICT,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(150) NOT NULL,
    credit_hours INT NOT NULL CHECK (credit_hours BETWEEN 1 AND 6),
    is_lab_required BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS academics.section (
    section_id SERIAL PRIMARY KEY,
    course_id INT NOT NULL REFERENCES academics.course(course_id) ON DELETE RESTRICT,
    semester_id INT NOT NULL REFERENCES academics.semester(semester_id) ON DELETE RESTRICT,
    teacher_id INT NOT NULL REFERENCES academics.teacher(teacher_id) ON DELETE RESTRICT,
    section_name VARCHAR(15) NOT NULL,
    max_capacity INT NOT NULL DEFAULT 40 CHECK (max_capacity BETWEEN 1 AND 150),
    enrolled_count INT NOT NULL DEFAULT 0 CHECK (enrolled_count >= 0),
    room_number VARCHAR(50) NOT NULL,
    CONSTRAINT uq_section_course_term UNIQUE (course_id, semester_id, section_name),
    CONSTRAINT chk_section_capacity CHECK (enrolled_count <= max_capacity)
);

CREATE TABLE IF NOT EXISTS academics.enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES academics.student(student_id) ON DELETE CASCADE,
    section_id INT NOT NULL REFERENCES academics.section(section_id) ON DELETE RESTRICT,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Enrolled' CHECK (status IN ('Enrolled', 'Completed', 'Dropped', 'Withdrawn')),
    final_grade VARCHAR(5) DEFAULT NULL CHECK (final_grade IN ('A', 'B+', 'B', 'C+', 'C', 'D', 'F', 'I', NULL)),
    gpa_points NUMERIC(3, 2) DEFAULT NULL CHECK (gpa_points BETWEEN 0.00 AND 4.00),
    CONSTRAINT uq_student_section UNIQUE (student_id, section_id)
);

CREATE TABLE IF NOT EXISTS academics.attendance (
    attendance_id BIGSERIAL PRIMARY KEY,
    enrollment_id INT NOT NULL REFERENCES academics.enrollment(enrollment_id) ON DELETE CASCADE,
    lecture_date DATE NOT NULL,
    status VARCHAR(15) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
    remarks VARCHAR(255),
    marked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_enrollment_lecture_date UNIQUE (enrollment_id, lecture_date)
);

CREATE TABLE IF NOT EXISTS academics.assessment (
    assessment_id SERIAL PRIMARY KEY,
    section_id INT NOT NULL REFERENCES academics.section(section_id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    assessment_type VARCHAR(20) NOT NULL CHECK (assessment_type IN ('Quiz', 'Assignment', 'Midterm', 'Final', 'Project', 'Lab_Viva')),
    max_marks NUMERIC(5, 2) NOT NULL CHECK (max_marks > 0),
    weightage_percent NUMERIC(5, 2) NOT NULL CHECK (weightage_percent BETWEEN 1 AND 100),
    due_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS academics.assessment_result (
    result_id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES academics.assessment(assessment_id) ON DELETE CASCADE,
    enrollment_id INT NOT NULL REFERENCES academics.enrollment(enrollment_id) ON DELETE CASCADE,
    marks_obtained NUMERIC(5, 2) NOT NULL CHECK (marks_obtained >= 0),
    remarks TEXT,
    graded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_assessment_enrollment UNIQUE (assessment_id, enrollment_id)
);

-- 3. FINANCE SCHEMA
CREATE TABLE IF NOT EXISTS finance.fee_structure (
    fee_structure_id SERIAL PRIMARY KEY,
    program_id INT NOT NULL REFERENCES academics.program(program_id) ON DELETE RESTRICT,
    semester_id INT NOT NULL REFERENCES academics.semester(semester_id) ON DELETE RESTRICT,
    tuition_fee NUMERIC(10, 2) NOT NULL CHECK (tuition_fee >= 0),
    lab_fee NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (lab_fee >= 0),
    library_fund NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (library_fund >= 0),
    exam_fee NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (exam_fee >= 0),
    total_structure_amount NUMERIC(10, 2) GENERATED ALWAYS AS (tuition_fee + lab_fee + library_fund + exam_fee) STORED,
    CONSTRAINT uq_fee_program_semester UNIQUE (program_id, semester_id)
);

CREATE TABLE IF NOT EXISTS finance.student_invoice (
    invoice_id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(40) NOT NULL UNIQUE,
    student_id INT NOT NULL REFERENCES academics.student(student_id) ON DELETE RESTRICT,
    semester_id INT NOT NULL REFERENCES academics.semester(semester_id) ON DELETE RESTRICT,
    fee_structure_id INT NOT NULL REFERENCES finance.fee_structure(fee_structure_id) ON DELETE RESTRICT,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    paid_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (paid_amount >= 0),
    balance_due NUMERIC(10, 2) NOT NULL CHECK (balance_due >= 0),
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Unpaid' CHECK (status IN ('Unpaid', 'Partial', 'Paid', 'Cancelled')),
    CONSTRAINT chk_invoice_dates CHECK (due_date >= issue_date),
    CONSTRAINT uq_student_invoice_term UNIQUE (student_id, semester_id)
);

CREATE TABLE IF NOT EXISTS finance.fee_payment (
    payment_id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL REFERENCES finance.student_invoice(invoice_id) ON DELETE RESTRICT,
    payment_reference VARCHAR(60) NOT NULL UNIQUE,
    amount_paid NUMERIC(10, 2) NOT NULL CHECK (amount_paid > 0),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('Bank_Transfer', 'Online_Portal', 'Cash_Challan', 'Credit_Card')),
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    received_by_user_id INT REFERENCES system_core.user_account(user_id) ON DELETE SET NULL,
    remarks TEXT
);

CREATE TABLE IF NOT EXISTS finance.fine (
    fine_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES academics.student(student_id) ON DELETE RESTRICT,
    fine_type VARCHAR(30) NOT NULL CHECK (fine_type IN ('Library_Overdue', 'Library_Damage', 'Late_Fee_Surcharge', 'Discipline', 'Lab_Breakage')),
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    reason TEXT NOT NULL,
    source_reference_id VARCHAR(50),
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. LIBRARY SCHEMA
CREATE TABLE IF NOT EXISTS library.book (
    book_id SERIAL PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    publisher VARCHAR(120),
    publication_year INT CHECK (publication_year BETWEEN 1800 AND 2100),
    category VARCHAR(60) NOT NULL DEFAULT 'General'
);

CREATE TABLE IF NOT EXISTS library.book_copy (
    copy_id SERIAL PRIMARY KEY,
    book_id INT NOT NULL REFERENCES library.book(book_id) ON DELETE RESTRICT,
    barcode VARCHAR(40) NOT NULL UNIQUE,
    edition VARCHAR(30) DEFAULT '1st Edition',
    shelf_location VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Available' CHECK (status IN ('Available', 'Issued', 'Under_Maintenance', 'Lost', 'Damaged'))
);

CREATE TABLE IF NOT EXISTS library.library_member (
    member_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES system_core.user_account(user_id) ON DELETE RESTRICT,
    membership_number VARCHAR(30) NOT NULL UNIQUE,
    member_type VARCHAR(20) NOT NULL CHECK (member_type IN ('Student', 'Faculty', 'Staff')),
    max_allowed_books INT NOT NULL DEFAULT 3 CHECK (max_allowed_books BETWEEN 1 AND 10),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    joined_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS library.book_issue (
    issue_id SERIAL PRIMARY KEY,
    copy_id INT NOT NULL REFERENCES library.book_copy(copy_id) ON DELETE RESTRICT,
    member_id INT NOT NULL REFERENCES library.library_member(member_id) ON DELETE RESTRICT,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    overdue_fine NUMERIC(8, 2) DEFAULT 0.00 CHECK (overdue_fine >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'Issued' CHECK (status IN ('Issued', 'Returned', 'Overdue', 'Lost')),
    CONSTRAINT chk_issue_dates CHECK (due_date >= issue_date)
);

-- 5. INVENTORY SCHEMA
CREATE TABLE IF NOT EXISTS inventory.item_category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS inventory.room_lab (
    room_id SERIAL PRIMARY KEY,
    dept_id INT NOT NULL REFERENCES academics.department(dept_id) ON DELETE RESTRICT,
    room_number VARCHAR(30) NOT NULL,
    room_name VARCHAR(100),
    room_type VARCHAR(30) NOT NULL CHECK (room_type IN ('Computer_Lab', 'Physics_Lab', 'Chemistry_Lab', 'Lecture_Hall', 'Faculty_Office', 'Store_Room')),
    capacity INT NOT NULL DEFAULT 30 CHECK (capacity > 0),
    CONSTRAINT uq_dept_room UNIQUE (dept_id, room_number)
);

CREATE TABLE IF NOT EXISTS inventory.inventory_item (
    item_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES inventory.item_category(category_id) ON DELETE RESTRICT,
    item_code VARCHAR(30) NOT NULL UNIQUE,
    item_name VARCHAR(120) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'Units',
    total_stock INT NOT NULL DEFAULT 0 CHECK (total_stock >= 0),
    available_stock INT NOT NULL DEFAULT 0 CHECK (available_stock >= 0),
    min_reorder_level INT NOT NULL DEFAULT 5 CHECK (min_reorder_level >= 0),
    CONSTRAINT chk_item_stock CHECK (available_stock <= total_stock)
);

CREATE TABLE IF NOT EXISTS inventory.purchase_order (
    po_id SERIAL PRIMARY KEY,
    po_number VARCHAR(40) NOT NULL UNIQUE,
    vendor_name VARCHAR(120) NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_cost NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (total_cost >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Received', 'Cancelled')),
    ordered_by_user_id INT REFERENCES system_core.user_account(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inventory.purchase_item (
    po_item_id SERIAL PRIMARY KEY,
    po_id INT NOT NULL REFERENCES inventory.purchase_order(po_id) ON DELETE CASCADE,
    item_id INT NOT NULL REFERENCES inventory.inventory_item(item_id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    line_total NUMERIC(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    CONSTRAINT uq_po_item UNIQUE (po_id, item_id)
);

CREATE TABLE IF NOT EXISTS inventory.item_issuance (
    issuance_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES inventory.inventory_item(item_id) ON DELETE RESTRICT,
    room_id INT NOT NULL REFERENCES inventory.room_lab(room_id) ON DELETE RESTRICT,
    issued_to_user_id INT NOT NULL REFERENCES system_core.user_account(user_id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    return_date DATE DEFAULT NULL,
    condition_notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'In_Use' CHECK (status IN ('In_Use', 'Returned', 'Damaged', 'Disposed'))
);

-- 6. AI SCHEMA
CREATE TABLE IF NOT EXISTS ai.conversation (
    conversation_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES system_core.user_account(user_id) ON DELETE CASCADE,
    session_title VARCHAR(120) NOT NULL DEFAULT 'Academic Assistant Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai.message (
    message_id BIGSERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES ai.conversation(conversation_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES system_core.user_account(user_id) ON DELETE RESTRICT,
    user_role VARCHAR(50) NOT NULL,
    user_query TEXT NOT NULL,
    generated_sql TEXT,
    execution_status VARCHAR(30) NOT NULL DEFAULT 'SUCCESS' CHECK (execution_status IN ('SUCCESS', 'REJECTED_SECURITY', 'SYNTAX_ERROR', 'EMPTY_RESULT')),
    row_count_returned INT DEFAULT 0,
    response_summary TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
