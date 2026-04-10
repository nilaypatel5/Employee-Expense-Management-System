# DAY 5 - Complete CRUD API + Advanced Endpoints

## Date: 10 April 2026

## 🎯 Goal

Build a **full-featured Expense Management API** with:

* PostgreSQL integration
* Complete CRUD operations
* Filters, pagination
* Dashboard analytics

---

## 🚀 What I Built Today

### ✅ 1. PostgreSQL Database Integration

* Connected Flask app with PostgreSQL using `psycopg2`
* Created reusable DB connection function
* Handled connection errors properly

---

### ✅ 2. Full CRUD for Expenses

| Operation | Method | Endpoint      | Description            |
| --------- | ------ | ------------- | ---------------------- |
| Create    | POST   | /expenses     | Add new expense        |
| Read All  | GET    | /expenses     | Get all expenses       |
| Read One  | GET    | /expenses/:id | Get single expense     |
| Update    | PUT    | /expenses/:id | Approve/Reject expense |
| Delete    | DELETE | /expenses/:id | Delete expense         |

---

### 🧪 Example API Tests

#### ➕ Create Expense

```bash
curl -X POST http://localhost:5000/expenses \
-H "Content-Type: application/json" \
-d '{
  "emp_id": 2,
  "category": "travel",
  "amount": 500,
  "description": "Flight booking",
  "expense_date": "2026-04-09"
}'
```

---

#### 🔄 Update Expense (Approve)

```bash
curl -X PUT http://localhost:5000/expenses/1 \
-H "Content-Type: application/json" \
-d '{
  "status": "approved",
  "approved_by": 1,
  "notes": "Approved quickly"
}'
```

---

#### ❌ Delete Expense

```bash
curl -X DELETE http://localhost:5000/expenses/1
```

---

## 🔍 3. Advanced Features

### 📌 Filters & Pagination

* Filter by:

  * status
  * category
  * emp_id
* Pagination:

  * page
  * per_page

👉 Example:

```bash
curl "http://localhost:5000/expenses?status=approved&page=1&per_page=10"
```

---

### 📊 Dashboard API

#### Endpoint:

```
GET /dashboard
```

#### Provides:

* Total expenses
* Total amount
* Average amount
* Category-wise stats
* Status breakdown
* Top spenders
* Department analysis

---

### 👥 Employee APIs

| Method | Endpoint       | Purpose          |
| ------ | -------------- | ---------------- |
| GET    | /employees     | List employees   |
| GET    | /employees/:id | Get one employee |

---

## 🛡️ 4. Validation & Error Handling

### Validation:

* Required fields check
* Amount must be positive
* Category validation
* Status validation

### Error Handling:

* 400 → Bad request
* 404 → Not found
* 500 → Server error

---

## 📈 What I Learned

* How to connect Flask with PostgreSQL
* Writing production-level REST APIs
* Implementing CRUD properly
* Handling real-world validation
* Building analytics endpoints
* Writing clean and structured backend code

---

## 🎉 Outcome

* Built complete backend API ✅
* Added database integration ✅
* Implemented CRUD operations ✅
* Added filters & pagination ✅
* Built dashboard analytics ✅

---
