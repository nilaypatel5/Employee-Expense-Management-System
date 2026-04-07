
# 📅 DAY 2: SQL Fundamentals – Real Questions with Answers
## Date: 07 April 2026

## 🎯 Goal

Writing SQL queries to answer real business questions using my actual data.

---

## 🛠️ Task 2.1: Basic SELECT & Filtering

### Question 1: "Show all expenses for Priya Patel"

```sql
-- Step 1: Get emp_id
SELECT emp_id FROM employees WHERE name = 'Priya Patel';
-- Result: 2

-- Step 2: Get expenses
SELECT * FROM expenses WHERE emp_id = 2;

-- Final (using JOIN)
SELECT 
    e.expense_id,
    emp.name,
    e.category,
    e.amount,
    e.status
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE emp.name = 'Priya Patel';
````

---

### Question 2: "Show all pending expenses"

```sql
SELECT 
    e.expense_id,
    emp.name,
    e.category,
    e.amount,
    e.submitted_date
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE e.status = 'pending'
ORDER BY e.submitted_date DESC;
```

---

## 📊 Task 2.2: Aggregations

### Question 3: "Total expenses per employee"

```sql
SELECT 
    emp.name,
    COUNT(e.expense_id) AS total_expenses,
    SUM(e.amount) AS total_spent
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
GROUP BY e.emp_id, emp.name
ORDER BY total_spent DESC;
```

---

### Question 4: "Total spending by category"

```sql
SELECT 
    category,
    COUNT(*) AS total_count,
    SUM(amount) AS total_amount
FROM expenses
GROUP BY category
ORDER BY total_amount DESC;
```

---

## 🔍 Task 2.3: HAVING

### Question 5: "Employees with more than 2 expenses"

```sql
SELECT 
    emp.name,
    COUNT(e.expense_id) AS expense_count
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
GROUP BY e.emp_id, emp.name
HAVING COUNT(e.expense_id) > 2;
```

---

## 📅 Task 2.4: Date Filtering

### Question 6: "Expenses in last 7 days"

```sql
SELECT 
    emp.name,
    e.category,
    e.amount,
    e.submitted_date
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE e.submitted_date >= NOW() - INTERVAL '7 days'
ORDER BY e.submitted_date DESC;
```

---

## 🧩 Task 2.5: Subqueries

### Question 7: "Expenses higher than category average"

```sql
SELECT 
    emp.name,
    e.category,
    e.amount
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE e.amount > (
    SELECT AVG(amount)
    FROM expenses
    WHERE category = e.category
);
```

---

## 🚀 Real-World Queries

### Question 1: "Show approved expenses with employee department"

```sql
SELECT 
    emp.name,
    emp.department,
    e.category,
    e.amount
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE e.status = 'approved';
```

---

### Question 2: "Who spent the most on travel?"

```sql
SELECT 
    emp.name,
    SUM(e.amount) AS total_travel
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE e.category = 'travel'
GROUP BY emp.name
ORDER BY total_travel DESC
LIMIT 1;
```

---

### Question 3: "Which manager approved the most expenses?"

```sql
SELECT 
    m.name AS manager_name,
    COUNT(e.expense_id) AS approvals
FROM expenses e
JOIN employees m ON e.approved_by = m.emp_id
GROUP BY m.name
ORDER BY approvals DESC;
```

---

## 🎉 Outcome

* Queries now match my real data ✅
* Answers are correct and easy to understand now ✅

---