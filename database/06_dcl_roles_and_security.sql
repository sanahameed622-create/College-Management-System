-- ============================================================================
-- AcademiaPro - Integrated College Management System
-- Module: 06_dcl_roles_and_security.sql
-- Description: DCL Roles, Grants, Revokes and AI Security Sandboxing
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'acad_admin_role') THEN
        CREATE ROLE acad_admin_role;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'acad_ai_readonly_role') THEN
        CREATE ROLE acad_ai_readonly_role;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA system_core, academics, finance, library, inventory, ai TO acad_admin_role, acad_ai_readonly_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA system_core, academics, finance, library, inventory, ai TO acad_admin_role;

-- AI READ-ONLY PERMISSIONS (Strictly Views only)
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA system_core, academics, finance, library, inventory FROM acad_ai_readonly_role;
GRANT SELECT ON academics.v_student_transcript, finance.v_defaulters, inventory.v_low_stock, library.v_overdue_books, academics.v_attendance_shortage TO acad_ai_readonly_role;
GRANT SELECT, INSERT ON ai.conversation, ai.message TO acad_ai_readonly_role;
