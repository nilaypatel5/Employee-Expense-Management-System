"""
Expense Management API 
Completed REST API with all CRUD operations using PostgreSQL
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import sql
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL connection config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'admin',
    'database': 'expense_system',
    'port': 5432
}

# DATABASE UTILITIES

def get_db():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f'Database connection error: {str(e)}')
        raise

def dict_from_row(cursor, row):
    """Convert psycopg2 row to dictionary using column names"""
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

# VALIDATION

def validate_expense(data):
    """Validate expense data"""
    errors = []
    
    # Required fields
    required = ['emp_id', 'category', 'amount', 'expense_date']
    for field in required:
        if field not in data:
            errors.append(f'{field} is required')
    
    # Validate amount
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                errors.append('amount must be positive')
        except (ValueError, TypeError):
            errors.append('amount must be a number')
    
    # Validate category
    valid_categories = ['travel', 'meals', 'office', 'other']
    if 'category' in data and data['category'] not in valid_categories:
        errors.append(f'category must be one of: {", ".join(valid_categories)}')
    
    # Validate status (for updates)
    if 'status' in data:
        valid_statuses = ['pending', 'approved', 'rejected']
        if data['status'] not in valid_statuses:
            errors.append(f'status must be one of: {", ".join(valid_statuses)}')
    
    return errors

# ERROR HANDLERS

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server error: {str(error)}')
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ENDPOINTS

# HEALTH CHECK
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'API is running', 'database': 'PostgreSQL'}), 200
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500

# EXPENSES ENDPOINTS

@app.route('/expenses', methods=['GET'])
def get_expenses():
    """
    GET /expenses
    List all expenses with optional filters
    
    Query Parameters:
        - status: pending, approved, rejected
        - category: travel, meals, office, other
        - emp_id: filter by employee ID
        - limit: max results (default 100)
        - page: for pagination
        - per_page: items per page (default 20)
    """
    conn = None
    try:
        # Get query parameters
        status = request.args.get('status')
        category = request.args.get('category')
        emp_id = request.args.get('emp_id')
        limit = request.args.get('limit', 100, type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = """
            SELECT e.expense_id, e.emp_id, emp.name as employee_name, 
                   e.category, e.amount, e.description, e.expense_date, 
                   e.submitted_date, e.status, e.approved_by, e.approval_date, e.notes
            FROM expenses e
            JOIN employees emp ON e.emp_id = emp.emp_id
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if status:
            query += " AND e.status = %s"
            params.append(status)
        
        if category:
            query += " AND e.category = %s"
            params.append(category)
        
        if emp_id:
            query += " AND e.emp_id = %s"
            params.append(int(emp_id))
        
        # Add ordering and limit
        query += " ORDER BY e.submitted_date DESC LIMIT %s OFFSET %s"
        offset = (page - 1) * per_page
        params.extend([limit, offset])
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM expenses WHERE 1=1"
        count_params = []
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
        if emp_id:
            count_query += " AND emp_id = %s"
            count_params.append(int(emp_id))
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
        
        # Convert rows to dicts
        columns = [desc[0] for desc in cursor.description]
        expenses = []
        cursor.execute(query, params)
        for row in cursor.fetchall():
            expenses.append(dict(zip([desc[0] for desc in cursor.description], row)))
        
        logger.info(f'GET /expenses: {len(expenses)} items returned')
        
        return jsonify({
            'success': True,
            'data': expenses,
            'count': len(expenses),
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    
    except Exception as e:
        logger.error(f'GET /expenses error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

@app.route('/expenses', methods=['POST'])
def create_expense():
    """
    POST /expenses
    Create a new expense
    
    Body:
    {
        "emp_id": 2,
        "category": "travel",
        "amount": 450.00,
        "description": "Flight to NYC",
        "expense_date": "2025-04-15"
    }
    """
    conn = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate
        errors = validate_expense(data)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if employee exists
        cursor.execute('SELECT emp_id FROM employees WHERE emp_id = %s', (data['emp_id'],))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Employee not found'}), 404
        
        # Insert expense
        cursor.execute("""
            INSERT INTO expenses (emp_id, category, amount, description, expense_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING expense_id
        """, (data['emp_id'], data['category'], data['amount'], 
              data.get('description'), data['expense_date']))
        
        expense_id = cursor.fetchone()[0]
        conn.commit()
        
        logger.info(f'Created expense {expense_id} for employee {data["emp_id"]}')
        
        return jsonify({
            'success': True,
            'message': 'Expense created successfully',
            'expense_id': expense_id
        }), 201
    
    except Exception as e:
        logger.error(f'POST /expenses error: {str(e)}')
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """GET /expenses/:id - Get single expense"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, emp.name as employee_name
            FROM expenses e
            JOIN employees emp ON e.emp_id = emp.emp_id
            WHERE e.expense_id = %s
        """, (expense_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Expense not found'}), 404
        
        columns = [desc[0] for desc in cursor.description]
        expense = dict(zip(columns, row))
        
        return jsonify({'success': True, 'data': expense}), 200
    
    except Exception as e:
        logger.error(f'GET /expenses/{expense_id} error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """
    PUT /expenses/:id
    Update expense status (approve/reject)
    
    Body:
    {
        "status": "approved",
        "approved_by": 1,
        "notes": "Looks good"
    }
    """
    conn = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['pending', 'approved', 'rejected']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'error': f'status must be one of: {", ".join(valid_statuses)}'
                }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if expense exists
        cursor.execute('SELECT * FROM expenses WHERE expense_id = %s', (expense_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Expense not found'}), 404
        
        # Build update query
        update_parts = []
        params = []
        
        if 'status' in data:
            update_parts.append('status = %s')
            params.append(data['status'])
        
        if 'approved_by' in data:
            update_parts.append('approved_by = %s')
            params.append(data['approved_by'])
        
        if 'notes' in data:
            update_parts.append('notes = %s')
            params.append(data['notes'])
        
        # Add approval_date if being approved
        if data.get('status') == 'approved':
            update_parts.append('approval_date = CURRENT_TIMESTAMP')
        
        if not update_parts:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        # Execute update
        update_query = 'UPDATE expenses SET ' + ', '.join(update_parts) + ' WHERE expense_id = %s'
        params.append(expense_id)
        
        cursor.execute(update_query, params)
        conn.commit()
        
        logger.info(f'Updated expense {expense_id}: {data}')
        
        return jsonify({
            'success': True,
            'message': 'Expense updated successfully'
        }), 200
    
    except Exception as e:
        logger.error(f'PUT /expenses/{expense_id} error: {str(e)}')
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """DELETE /expenses/:id - Delete expense"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute('SELECT * FROM expenses WHERE expense_id = %s', (expense_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Expense not found'}), 404
        
        # Delete
        cursor.execute('DELETE FROM expenses WHERE expense_id = %s', (expense_id,))
        conn.commit()
        
        logger.info(f'Deleted expense {expense_id}')
        
        return jsonify({'success': True, 'message': 'Expense deleted'}), 200
    
    except Exception as e:
        logger.error(f'DELETE /expenses/{expense_id} error: {str(e)}')
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

# DASHBOARD & ANALYTICS

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    GET /dashboard
    Get summary statistics and analytics
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_expenses,
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(AVG(amount), 0) as avg_amount
            FROM expenses
        """)
        row = cursor.fetchone()
        stats = {
            'total_expenses': row[0],
            'total_amount': float(row[1]),
            'avg_amount': float(row[2])
        }
        
        # By category
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(amount) as total, AVG(amount) as avg
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """)
        by_category = []
        for row in cursor.fetchall():
            by_category.append({
                'category': row[0],
                'count': row[1],
                'total': float(row[2]),
                'avg': float(row[3])
            })
        
        # By status
        cursor.execute("""
            SELECT status, COUNT(*) as count, SUM(amount) as total
            FROM expenses
            GROUP BY status
        """)
        by_status = []
        for row in cursor.fetchall():
            by_status.append({
                'status': row[0],
                'count': row[1],
                'total': float(row[2])
            })
        
        # Top spenders
        cursor.execute("""
            SELECT emp.name, COUNT(*) as expense_count, SUM(e.amount) as total
            FROM expenses e
            JOIN employees emp ON e.emp_id = emp.emp_id
            GROUP BY e.emp_id, emp.name
            ORDER BY total DESC
            LIMIT 5
        """)
        top_spenders = []
        for row in cursor.fetchall():
            top_spenders.append({
                'name': row[0],
                'expense_count': row[1],
                'total': float(row[2])
            })
        
        # By department
        cursor.execute("""
            SELECT emp.department, COUNT(*) as expense_count, SUM(e.amount) as total
            FROM expenses e
            JOIN employees emp ON e.emp_id = emp.emp_id
            GROUP BY emp.department
            ORDER BY total DESC
        """)
        by_department = []
        for row in cursor.fetchall():
            by_department.append({
                'department': row[0],
                'expense_count': row[1],
                'total': float(row[2])
            })
        
        # Approval stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviewed,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_count,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count
            FROM expenses
        """)
        row = cursor.fetchone()
        approval_stats = {
            'total_reviewed': row[0],
            'approved_count': row[1],
            'rejected_count': row[2],
            'pending_count': row[3]
        }
        
        logger.info('GET /dashboard')
        
        return jsonify({
            'success': True,
            'stats': stats,
            'by_category': by_category,
            'by_status': by_status,
            'by_department': by_department,
            'top_spenders': top_spenders,
            'approval_stats': approval_stats
        }), 200
    
    except Exception as e:
        logger.error(f'GET /dashboard error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

# EMPLOYEES ENDPOINTS

@app.route('/employees', methods=['GET'])
def get_employees():
    """GET /employees - List all employees"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees ORDER BY name")
        
        employees = []
        for row in cursor.fetchall():
            columns = [desc[0] for desc in cursor.description]
            employees.append(dict(zip(columns, row)))
        
        return jsonify({'success': True, 'data': employees, 'count': len(employees)}), 200
    
    except Exception as e:
        logger.error(f'GET /employees error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

@app.route('/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    """GET /employees/:id - Get single employee"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM employees WHERE emp_id = %s', (emp_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'success': False, 'error': 'Employee not found'}), 404
        
        columns = [desc[0] for desc in cursor.description]
        employee = dict(zip(columns, row))
        
        return jsonify({'success': True, 'data': employee}), 200
    
    except Exception as e:
        logger.error(f'GET /employees/{emp_id} error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if conn:
            conn.close()

# RUN SERVER

if __name__ == '__main__':
    print("Expense Management API")
    print("=" * 50)
    print("Server running on: http://localhost:5000")
    print("\n Available endpoints:")
    print("   GET    /health")
    print("   GET    /expenses (list with filters)")
    print("   POST   /expenses (create)")
    print("   GET    /expenses/:id (get one)")
    print("   PUT    /expenses/:id (update status)")
    print("   DELETE /expenses/:id (delete)")
    print("   GET    /dashboard (analytics)")
    print("   GET    /employees (list)")
    print("   GET    /employees/:id (get one)")
    print("\n Test with: curl http://localhost:5000/health")
    print("=" * 50 + "\n")
    
    app.run(debug=True, port=5000)
