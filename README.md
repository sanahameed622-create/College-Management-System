# AcademiaPro - Integrated College Management System
**Academic DBMS Semester Project & Production Relational Architecture**

---

## 📌 Executive Summary

**AcademiaPro** is a comprehensive, normalized Relational Database Management System (RDBMS) and web application designed strictly according to university lecture guidelines, relational algebra principles, and academic feedback.

It features **6 modular schemas**, **25 fully normalized relational tables (in BCNF)**, automated triggers, transactional procedures, analytical views, and an interactive web dashboard with an AI Assistant sandbox.

---

## 🏛️ Schema Architecture (6 Logical Schemas)

1. **`system_core`**:
   - `role`, `user_account`, `user_role`, `audit_log` (forensic audit trail tracking all modifications)
2. **`academics`**:
   - `department`, `program`, `semester`, `teacher`, `student`, `course`, `section`, `enrollment`, `attendance`, `assessment`, `assessment_result`
   - *Key distinction:* Assessments (Quizzes, Midterms, Finals) are decoupled from Results for maximum structural flexibility.
3. **`finance`**:
   - `fee_structure`, `student_invoice`, `fee_payment`, `fine`
   - *Key integration:* Library overdue fines and discipline penalties consolidate seamlessly into student financial liability.
4. **`library`**:
   - `book`, `book_copy` (physical barcoded copies), `library_member`, `book_issue`
5. **`inventory`**:
   - `item_category`, `room_lab` (linked to academic departments), `inventory_item`, `purchase_order`, `purchase_item`, `item_issuance`
6. **`ai`**:
   - `conversation`, `message` (strict read-only SELECT assistant logging `user_id`, `role`, `generated_sql`, `execution_status`, `timestamp`)

---

## 🚀 How to Run Locally in VS Code (Step-by-Step Terminal Commands)

### Step 1: Open VS Code in the Project Folder
Open VS Code, press `Ctrl + ~` (or `Terminal -> New Terminal`), and navigate to this folder:
```powershell
cd "C:\Users\Sana Hameed Hacker\.gemini\antigravity\scratch\college_management_system"
```

### Step 2: Install Python Dependencies (If not already installed)
```powershell
pip install -r requirements.txt
```
*(Dependencies: `flask`, `psycopg2-binary`)*

### Step 3: Initialize the Database (One-Click)
Run the automated initialization script:
```powershell
python database\init_db.py
```
This script creates all schemas, tables, constraints, analytical views, and populates 25+ rows of realistic academic sample data.

### Step 4: Start the Web Application
```powershell
python app\app.py
```

### Step 5: Open in Your Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🐘 Optional: Running Native Scripts in PostgreSQL (psql / pgAdmin 4)

If your professor requests execution directly on a PostgreSQL server:

### Option A: Using PostgreSQL `psql` in Terminal
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f database\01_schema_ddl.sql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f database\02_views.sql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f database\03_triggers_and_procedures.sql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f database\04_sample_data.sql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f database\05_complex_queries.sql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -f database\06_dcl_roles_and_security.sql
```

### Option B: Using pgAdmin 4 Query Tool
1. Open **pgAdmin 4** and connect to your database.
2. Open the **Query Tool**.
3. Open and run the scripts in sequence:
   1. `01_schema_ddl.sql`
   2. `02_views.sql`
   3. `03_triggers_and_procedures.sql`
   4. `04_sample_data.sql`
   5. `05_complex_queries.sql`
   6. `06_dcl_roles_and_security.sql`

---

## 📑 Relational Theory, Keys & Normalization Summary

A full theoretical monograph is provided in [`docs/RELATIONAL_THEORY_AND_NORMALIZATION.md`](file:///C:/Users/Sana%20Hameed%20Hacker/.gemini/antigravity/scratch/college_management_system/docs/RELATIONAL_THEORY_AND_NORMALIZATION.md).

### 1. Keys Classification
* **Primary Keys (PK):** Unique identifier for every table (e.g., `student_id`, `course_id`, `invoice_id`).
* **Candidate Keys (CK):** Minimal superkeys with uniqueness (e.g., `{student_id}`, `{roll_number}`, `{cnic}`, `{email}`).
* **Foreign Keys (FK):** Strict referential integrity links enforcing `ON DELETE RESTRICT` or `ON DELETE CASCADE`.

### 2. Functional Dependencies (FDs)
* Every table has explicit functional dependencies formalized (e.g. `roll_number -> {first_name, last_name, program_id, email, cnic}`).

### 3. Anomalies Resolved
* **Insertion Anomaly:** Overcome by separating Teacher and Department from Enrollment; new staff can be recorded without students.
* **Deletion Anomaly:** Deleting a student enrollment retains the Course, Teacher, and Department entities intact.
* **Update Anomaly:** Single-row updates for shared attributes (e.g. professor office or course title) prevent data inconsistency.

### 4. Normalization (1NF &rarr; 2NF &rarr; 3NF &rarr; BCNF)
* **1NF:** Multi-valued phone numbers and course arrays flattened into atomic values.
* **2NF:** Eliminated partial dependencies on composite keys in `ENROLLMENT` and `ASSESSMENT_RESULT`.
* **3NF:** Eliminated transitive dependencies ($Student \rightarrow Program \rightarrow Department$).
* **BCNF:** Certified that every non-trivial determinant $X \rightarrow Y$ has $X$ as a superkey.

---

## 🤖 AI Assistant Security Architecture

* **Role:** Sandboxed read-only assistant (`acad_ai_readonly_role`).
* **Privilege:** Only `SELECT` queries on analytical views (`v_student_transcript`, `v_defaulters`, `v_low_stock`, `v_overdue_books`, `v_attendance_shortage`).
* **Audit:** Every inquiry logs `user_id`, `user_role`, `user_query`, `generated_sql`, `execution_status`, `row_count_returned`, and `timestamp` into `ai.message`.
* **Non-SELECT Interception:** Any `INSERT`, `UPDATE`, `DELETE`, `DROP`, or `ALTER` is strictly intercepted and blocked.

---

## 📁 Project Directory Map

```
college_management_system/
├── app/
│   ├── app.py                     # Flask Web Application Server
│   ├── database_engine.py         # Dual Engine (PostgreSQL / SQLite)
│   ├── static/                    # Custom Stylesheets & Assets
│   └── templates/                 # UI Templates
│       ├── base.html              # Modern responsive navbar & layout
│       ├── index.html             # Dashboard with KPIs & Relational Alerts
│       ├── academics.html         # Transcripts, Sections, 75% Attendance Check
│       ├── finance.html           # Invoices, Payments, Defaulters List
│       ├── library.html           # Catalog, Copies, Overdue Fine Calculator
│       ├── inventory.html         # Labs, Stock Reorder Levels, Asset Issuance
│       ├── ai_assistant.html      # Safe Read-Only AI Query Console & Audit
│       ├── security_audit.html    # RBAC Privileges Matrix & Audit Trail
│       ├── theory_docs.html       # Interactive Normalization & Keys Monograph
│       └── query_runner.html      # SQL Sandbox (Division, Difference, HAVING)
├── database/
│   ├── 01_schema_ddl.sql          # 6 Schemas DDL with Constraints
│   ├── 02_views.sql               # Core Analytical & AI Views
│   ├── 03_triggers_and_procedures.sql # Concurrency, Fines & Stock Triggers
│   ├── 04_sample_data.sql         # 25+ Rows Sample Data per Table
│   ├── 05_complex_queries.sql     # Relational Division, EXCEPT, CTEs
│   ├── 06_dcl_roles_and_security.sql # RBAC Grants, Revokes & RLS
│   └── init_db.py                 # Automated Database Setup Script
├── docs/
│   └── RELATIONAL_THEORY_AND_NORMALIZATION.md # Theoretical Monograph
├── requirements.txt               # Dependencies
├── run.bat                        # Windows CMD 1-click launcher
├── run.ps1                        # Windows PowerShell 1-click launcher
└── README.md                      # Documentation & Instructions
```
