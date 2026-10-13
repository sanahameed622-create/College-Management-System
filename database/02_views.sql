-- ============================================================================
-- AcademiaPro - Integrated College Management System
-- Module: 02_views.sql
-- Description: Analytical, Financial, Administrative and Secure AI Views
-- ============================================================================

CREATE OR REPLACE VIEW academics.v_student_transcript AS
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
FROM academics.student s
JOIN academics.program p ON s.program_id = p.program_id
JOIN academics.enrollment e ON s.student_id = e.student_id
JOIN academics.section sec ON e.section_id = sec.section_id
JOIN academics.course c ON sec.course_id = c.course_id
JOIN academics.semester sem ON sec.semester_id = sem.semester_id;

CREATE OR REPLACE VIEW finance.v_defaulters AS
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
        WHEN CURRENT_DATE > inv.due_date THEN 'Overdue Defaulter'
        ELSE 'Pending Payment'
    END AS defaulter_status
FROM finance.student_invoice inv
JOIN academics.student s ON inv.student_id = s.student_id
JOIN academics.program p ON s.program_id = p.program_id
JOIN academics.semester sem ON inv.semester_id = sem.semester_id
LEFT JOIN (
    SELECT student_id, SUM(amount) AS total_unpaid_fines
    FROM finance.fine
    WHERE is_paid = FALSE
    GROUP BY student_id
) fn ON s.student_id = fn.student_id
WHERE inv.balance_due > 0;

CREATE OR REPLACE VIEW inventory.v_low_stock AS
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
    COALESCE(
        STRING_AGG(DISTINCT d.dept_code || ' - ' || rl.room_number, ', '),
        'Central Store'
    ) AS deployed_locations
FROM inventory.inventory_item itm
JOIN inventory.item_category cat ON itm.category_id = cat.category_id
LEFT JOIN inventory.item_issuance isi ON itm.item_id = isi.item_id AND isi.status = 'In_Use'
LEFT JOIN inventory.room_lab rl ON isi.room_id = rl.room_id
LEFT JOIN academics.department d ON rl.dept_id = d.dept_id
WHERE itm.available_stock <= itm.min_reorder_level
GROUP BY itm.item_id, itm.item_code, itm.item_name, cat.category_name, itm.unit_of_measure, itm.total_stock, itm.available_stock, itm.min_reorder_level;

CREATE OR REPLACE VIEW library.v_overdue_books AS
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
    CURRENT_DATE - bi.due_date AS days_overdue,
    ROUND(((CURRENT_DATE - bi.due_date) * 10.00), 2) AS calculated_fine
FROM library.book_issue bi
JOIN library.book_copy bc ON bi.copy_id = bc.copy_id
JOIN library.book b ON bc.book_id = b.book_id
JOIN library.library_member lm ON bi.member_id = lm.member_id
JOIN system_core.user_account ua ON lm.user_id = ua.user_id
WHERE bi.status = 'Issued' AND CURRENT_DATE > bi.due_date;

CREATE OR REPLACE VIEW academics.v_attendance_shortage AS
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
        (COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
         NULLIF(COUNT(a.attendance_id), 0)::NUMERIC) * 100.00, 2
    ) AS attendance_percentage,
    CASE 
        WHEN ROUND((COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / NULLIF(COUNT(a.attendance_id), 0)::NUMERIC) * 100.00, 2) < 75.00
        THEN 'DEBARRED_FROM_FINAL_EXAM'
        ELSE 'ELIGIBLE'
    END AS examination_eligibility
FROM academics.student s
JOIN academics.enrollment e ON s.student_id = e.student_id
JOIN academics.section sec ON e.section_id = sec.section_id
JOIN academics.course c ON sec.course_id = c.course_id
LEFT JOIN academics.attendance a ON e.enrollment_id = a.enrollment_id
GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name, c.course_code, c.title, sec.section_name;
