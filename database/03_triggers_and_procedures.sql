-- ============================================================================
-- AcademiaPro - Integrated College Management System
-- Module: 03_triggers_and_procedures.sql
-- Description: Triggers, Concurrency Protections, Stored Procedures, Transactions
-- ============================================================================

-- 1. CONCURRENCY-SAFE ENROLLMENT CAPACITY CHECK
CREATE OR REPLACE FUNCTION academics.fn_check_section_capacity_and_increment()
RETURNS TRIGGER AS $$
DECLARE
    v_max_cap INT;
    v_curr_count INT;
BEGIN
    SELECT max_capacity, enrolled_count
    INTO v_max_cap, v_curr_count
    FROM academics.section
    WHERE section_id = NEW.section_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Section ID % does not exist', NEW.section_id;
    END IF;

    IF v_curr_count >= v_max_cap THEN
        RAISE EXCEPTION 'Cannot enroll student %. Section % has reached maximum capacity of % seats.',
            NEW.student_id, NEW.section_id, v_max_cap;
    END IF;

    UPDATE academics.section
    SET enrolled_count = enrolled_count + 1
    WHERE section_id = NEW.section_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_enrollment_capacity ON academics.enrollment;
CREATE TRIGGER trg_check_enrollment_capacity
BEFORE INSERT ON academics.enrollment
FOR EACH ROW
EXECUTE FUNCTION academics.fn_check_section_capacity_and_increment();

-- 2. LIBRARY FINE AUTO-SYNC TO FINANCE
CREATE OR REPLACE FUNCTION library.fn_sync_library_fine_to_finance()
RETURNS TRIGGER AS $$
DECLARE
    v_student_id INT;
    v_days_overdue INT;
    v_daily_rate NUMERIC := 10.00;
    v_calc_fine NUMERIC := 0.00;
BEGIN
    IF NEW.return_date IS NOT NULL AND NEW.return_date > NEW.due_date THEN
        v_days_overdue := (NEW.return_date - NEW.due_date);
        v_calc_fine := v_days_overdue * v_daily_rate;
        NEW.overdue_fine := v_calc_fine;
        NEW.status := 'Returned';

        SELECT s.student_id INTO v_student_id
        FROM library.library_member lm
        JOIN academics.student s ON lm.user_id = s.user_id
        WHERE lm.member_id = NEW.member_id;

        IF v_student_id IS NOT NULL AND v_calc_fine > 0 THEN
            INSERT INTO finance.fine (
                student_id, fine_type, amount, reason, source_reference_id, is_paid, created_at
            ) VALUES (
                v_student_id, 'Library_Overdue', v_calc_fine,
                'Overdue fine for book copy barcode: ' || (SELECT barcode FROM library.book_copy WHERE copy_id = NEW.copy_id),
                'ISSUE-' || NEW.issue_id, FALSE, CURRENT_TIMESTAMP
            );
        END IF;

        UPDATE library.book_copy
        SET status = 'Available'
        WHERE copy_id = NEW.copy_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_library_fine ON library.book_issue;
CREATE TRIGGER trg_sync_library_fine
BEFORE UPDATE ON library.book_issue
FOR EACH ROW
EXECUTE FUNCTION library.fn_sync_library_fine_to_finance();

-- 3. INVENTORY STOCK DEDUCTION TRIGGER
CREATE OR REPLACE FUNCTION inventory.fn_deduct_inventory_stock()
RETURNS TRIGGER AS $$
DECLARE
    v_available INT;
BEGIN
    SELECT available_stock INTO v_available
    FROM inventory.inventory_item
    WHERE item_id = NEW.item_id
    FOR UPDATE;

    IF v_available < NEW.quantity THEN
        RAISE EXCEPTION 'Insufficient inventory for item ID %. Available: %, Requested: %',
            NEW.item_id, v_available, NEW.quantity;
    END IF;

    UPDATE inventory.inventory_item
    SET available_stock = available_stock - NEW.quantity
    WHERE item_id = NEW.item_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_deduct_inventory_stock ON inventory.item_issuance;
CREATE TRIGGER trg_deduct_inventory_stock
BEFORE INSERT ON inventory.item_issuance
FOR EACH ROW
EXECUTE FUNCTION inventory.fn_deduct_inventory_stock();
