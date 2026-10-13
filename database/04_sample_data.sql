-- ============================================================================
-- AcademiaPro - Integrated College Management System
-- Module: 04_sample_data.sql
-- Description: 25+ realistic sample rows across all relational schemas
-- ============================================================================

INSERT INTO system_core.role (role_id, role_name, description) VALUES
(1, 'Admin', 'System Administrator with full superuser privileges'),
(2, 'Teacher', 'Academic faculty member with grading and attendance rights'),
(3, 'Student', 'Enrolled student with view access to transcripts, fee, library'),
(4, 'Accountant', 'Finance officer managing fee invoices, payments, and fines'),
(5, 'Librarian', 'Library manager handling books catalog and circulation'),
(6, 'StoreKeeper', 'Inventory manager tracking equipment, stock, and room issuances'),
(7, 'AI_Agent', 'Read-only automated assistant role querying analytical views')
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO system_core.user_account (user_id, username, email, password_hash, full_name) VALUES
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
(20, 'std_saad_iqbal', 'saad.iqbal@student.edu.pk', 'pbkdf2:sha256:std123', 'Saad Iqbal')
ON CONFLICT (username) DO NOTHING;

INSERT INTO academics.department (dept_id, dept_code, dept_name, office_location, contact_email) VALUES
(1, 'CS', 'Department of Computer Science', 'Block A, 2nd Floor', 'cs@academiapro.edu.pk'),
(2, 'SE', 'Department of Software Engineering', 'Block A, 3rd Floor', 'se@academiapro.edu.pk'),
(3, 'EE', 'Department of Electrical Engineering', 'Block B, 1st Floor', 'ee@academiapro.edu.pk'),
(4, 'MS', 'Department of Management Sciences', 'Block C, Ground Floor', 'ms@academiapro.edu.pk')
ON CONFLICT (dept_code) DO NOTHING;

INSERT INTO academics.program (program_id, dept_id, program_code, program_name, degree_level, total_semesters, total_credits) VALUES
(1, 1, 'BSCS', 'Bachelor of Science in Computer Science', 'Undergraduate', 8, 134),
(2, 2, 'BSSE', 'Bachelor of Science in Software Engineering', 'Undergraduate', 8, 136),
(3, 1, 'BSAI', 'Bachelor of Science in Artificial Intelligence', 'Undergraduate', 8, 130),
(4, 4, 'BBA', 'Bachelor of Business Administration', 'Undergraduate', 8, 132)
ON CONFLICT (program_code) DO NOTHING;

INSERT INTO academics.semester (semester_id, term_name, academic_year, start_date, end_date, is_current) VALUES
(1, 'Fall', 2025, '2025-09-01', '2026-01-20', FALSE),
(2, 'Spring', 2026, '2026-02-01', '2026-06-25', TRUE),
(3, 'Fall', 2026, '2026-09-01', '2027-01-20', FALSE)
ON CONFLICT (term_name, academic_year) DO NOTHING;

INSERT INTO academics.teacher (teacher_id, employee_code, user_id, dept_id, first_name, last_name, email, phone, designation, qualification) VALUES
(1, 'EMP-101', 2, 1, 'Tariq', 'Mahmood', 'tariq.mahmood@academiapro.edu.pk', '0300-1234567', 'Professor', 'PhD Computer Science'),
(2, 'EMP-102', 3, 1, 'Sarah', 'Khan', 'sarah.khan@academiapro.edu.pk', '0300-2345678', 'Associate Professor', 'PhD Software Engineering'),
(3, 'EMP-103', 4, 2, 'Usman', 'Ali', 'usman.ali@academiapro.edu.pk', '0300-3456789', 'Lecturer', 'MS Computer Science'),
(4, 'EMP-104', 5, 4, 'Farooq', 'Azam', 'farooq.azam@academiapro.edu.pk', '0300-4567890', 'Professor', 'PhD Finance')
ON CONFLICT (employee_code) DO NOTHING;

INSERT INTO academics.student (student_id, roll_number, user_id, program_id, first_name, last_name, email, cnic, phone, date_of_birth, admission_date, current_semester_num, status) VALUES
(1, 'BSCS-22-01', 10, 1, 'Ali', 'Khan', 'ali.khan@student.edu.pk', '35201-1111111-1', '0321-1000001', '2004-03-15', '2022-09-10', 4, 'Active'),
(2, 'BSCS-22-02', 11, 1, 'Bilal', 'Ahmed', 'bilal.ahmed@student.edu.pk', '35201-2222222-2', '0321-2000002', '2004-06-20', '2022-09-10', 4, 'Active'),
(3, 'BSCS-22-03', 12, 1, 'Fatima', 'Zahra', 'fatima.zahra@student.edu.pk', '35201-3333333-3', '0321-3000003', '2005-01-10', '2022-09-10', 4, 'Active'),
(4, 'BSSE-22-01', 13, 2, 'Hamza', 'Tariq', 'hamza.tariq@student.edu.pk', '35201-4444444-4', '0321-4000004', '2003-11-25', '2022-09-10', 4, 'Active'),
(5, 'BSSE-22-02', 14, 2, 'Zainab', 'Bibi', 'zainab.bibi@student.edu.pk', '35201-5555555-5', '0321-5000005', '2004-08-14', '2022-09-10', 4, 'Active')
ON CONFLICT (roll_number) DO NOTHING;

INSERT INTO academics.course (course_id, program_id, course_code, title, credit_hours, is_lab_required, description) VALUES
(1, 1, 'CS-201', 'Database Systems', 4, TRUE, 'Relational model, SQL, normalization.'),
(2, 1, 'CS-202', 'Data Structures & Algorithms', 4, TRUE, 'Stacks, queues, trees, graphs.'),
(3, 1, 'CS-301', 'Operating Systems', 4, TRUE, 'Processes, memory, file systems.')
ON CONFLICT (course_code) DO NOTHING;
