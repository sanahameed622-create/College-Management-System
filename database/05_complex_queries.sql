-- ============================================================================
-- AcademiaPro - Integrated College Management System
-- Module: 05_complex_queries.sql
-- Description: Advanced Relational SQL Queries (Division, Difference, HAVING, Window Functions)
-- ============================================================================

-- 1. RELATIONAL DIVISION: Students enrolled in all CS core courses
SELECT s.student_id, s.roll_number, s.first_name || ' ' || s.last_name AS student_name
FROM academics.student s
JOIN academics.program p ON s.program_id = p.program_id
WHERE p.program_code = 'BSCS'
  AND NOT EXISTS (
      SELECT c.course_id 
      FROM academics.course c 
      WHERE c.course_code IN ('CS-201', 'CS-202')
      EXCEPT
      SELECT sec.course_id
      FROM academics.enrollment e
      JOIN academics.section sec ON e.section_id = sec.section_id
      WHERE e.student_id = s.student_id
  );

-- 2. SET DIFFERENCE (EXCEPT): Students who have never borrowed any library book
SELECT s.student_id, s.roll_number, s.first_name || ' ' || s.last_name AS student_name
FROM academics.student s
WHERE s.status = 'Active'
EXCEPT
SELECT s.student_id, s.roll_number, s.first_name || ' ' || s.last_name
FROM academics.student s
JOIN library.library_member lm ON s.user_id = lm.user_id
JOIN library.book_issue bi ON lm.member_id = bi.member_id;

-- 3. AGGREGATION WITH HAVING: Sections with average assessment mark below 70%
SELECT c.course_code, c.title, sec.section_name, ROUND(AVG(ar.marks_obtained), 2) AS average_score
FROM academics.assessment a
JOIN academics.section sec ON a.section_id = sec.section_id
JOIN academics.course c ON sec.course_id = c.course_id
JOIN academics.assessment_result ar ON a.assessment_id = ar.assessment_id
GROUP BY c.course_code, c.title, sec.section_name
HAVING COUNT(ar.result_id) >= 2;
