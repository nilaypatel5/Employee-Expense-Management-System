-- schema.sql
-- Employee Expense Management System
-- Day 1: Create Tables & Indexes 

-- ============================
-- Create Employees Table
-- ============================
CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    manager_id INTEGER REFERENCES employees(emp_id),
    salary DECIMAL(10, 2),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- Create Expenses Table
-- ============================
CREATE TABLE expenses (
    expense_id SERIAL PRIMARY KEY,
    emp_id INTEGER NOT NULL REFERENCES employees(emp_id),
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    receipt_url VARCHAR(255),
    expense_date DATE NOT NULL,
    submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected')),
    approved_by INTEGER REFERENCES employees(emp_id),
    approval_date TIMESTAMP,
    notes TEXT
);

-- ============================
-- Create Departments Table
-- ============================
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) UNIQUE NOT NULL,
    budget DECIMAL(12, 2),
    manager_id INTEGER REFERENCES employees(emp_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- Create Indexes for Expenses
-- ============================
CREATE INDEX idx_emp_id ON expenses(emp_id);
CREATE INDEX idx_status ON expenses(status);
CREATE INDEX idx_category ON expenses(category);
CREATE INDEX idx_expense_date ON expenses(expense_date);
CREATE INDEX idx_submitted_date ON expenses(submitted_date);