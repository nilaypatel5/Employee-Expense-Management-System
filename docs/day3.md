# 📅 DAY 3: Query Practice – Real Data Insights

## Date: 08 April 2026

## 🎯 Goal

Practice SQL queries using real data and understand how to extract meaningful insights.

---

### Query 1: Total Spending by Category

```sql
SELECT 
    category,
    COUNT(*) AS expense_count,
    SUM(amount) AS total_spent,
    AVG(amount) AS average_expense
FROM expenses
GROUP BY category
ORDER BY total_spent DESC;
```

---

### Query 2: Spending by Employee

```sql
SELECT 
    emp.name AS employee_name,
    COUNT(e.expense_id) AS total_expenses,
    SUM(e.amount) AS total_spent,
    AVG(e.amount) AS avg_per_expense
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
GROUP BY e.emp_id, emp.name
ORDER BY total_spent DESC;
```

---

### Query 3: Spending by Department

```sql
SELECT 
    emp.department,
    COUNT(e.expense_id) AS num_expenses,
    SUM(e.amount) AS total_spending
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
GROUP BY emp.department
ORDER BY total_spending DESC;
```

---

### Query 4: Approval Status Breakdown

```sql
SELECT 
    status,
    COUNT(*) AS expense_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM expenses
GROUP BY status
ORDER BY expense_count DESC;
```

---

### Query 5: High Value Expenses (Above ₹3000)

```sql
SELECT 
    emp.name,
    e.category,
    e.amount,
    e.status
FROM expenses e
JOIN employees emp ON e.emp_id = emp.emp_id
WHERE e.amount > 3000
ORDER BY e.amount DESC;
```

---

## 📊 Expected Results Summary (Based on Data)

### Query 1 (Category)

* Travel → highest total
* Meals → medium
* Office → lowest

---

### Query 2 (Employee)

* Rajesh Verma → highest total
* Priya Patel → most entries
* Others → smaller contributions

---

### Query 3 (Department)

* Sales → highest
* Engineering → close
* HR / Finance → low

---

### Query 4 (Status)

* Approved → highest count
* Pending → next
* Rejected → lowest

---

### Query 5 (High Value)

* Rajesh Verma (₹15000)
* Priya Patel (₹8500)
* Neha Gupta (₹4200)

---

## 🎯 Pattern to Remember

```sql
SELECT 
    column,
    COUNT(*),
    SUM(amount),
    AVG(amount)
FROM table
GROUP BY column
ORDER BY SUM(amount) DESC;
```

---

## 🎉 Outcome

* Practiced real SQL queries on actual data ✅
* Understood how to analyze spending patterns ✅
* Built foundation for API-level queries ✅

---
