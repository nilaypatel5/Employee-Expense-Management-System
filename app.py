"""
Expense Management API 
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection info
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'admin',
    'database': 'expense_system',
    'port': 5432
}

# CONNECT TO DATABASE

def get_db():
    """Connect to PostgreSQL database"""
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
        logger.error(f'Cannot connect to database: {str(e)}')
        raise

# HELPER FUNCTION: Convert database rows to dictionaries# ============================================================================

def rows_to_dicts(cursor, rows):
    """Convert database rows to Python dictionaries"""
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]

# ENDPOINT 1: Health Check (Is API alive?)

@app.route('/health', methods=['GET'])
def health():
    """Check if API is working"""
    try:
        conn = get_db()
        conn.close()
        return jsonify({
            'success': True, 
            'message': 'API is running',
            'database': 'PostgreSQL'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': 'Database not connected'
        }), 500

# ENDPOINT 2: Get All Expenses

@app.route('/expenses', methods=['GET'])
def get_all_expenses():
    """Get all expenses"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                e.expense_id,
                e.emp_id,
                emp.name as employee_name,
                e.category,
                e.amount,
                e.expense_date,
                e.status
            FROM expenses e
            JOIN employees emp ON e.emp_id = emp.emp_id
            ORDER BY e.expense_date DESC
        """)
        rows = cursor.fetchall()
        expenses = rows_to_dicts(cursor, rows)
        cursor.close()
        logger.info(f'Returned {len(expenses)} expenses')
        return jsonify({'success': True, 'data': expenses, 'total': len(expenses)}), 200
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# START SERVER

if __name__ == '__main__':
    print("\n" + "="*50)
    print("EXPENSE API -  ENDPOINTS")
    print("="*50)
    print("\nServer running: http://localhost:5000")
    print("\AVAILABLE ENDPOINTS:\n")
    
    print("1️.  Health Check:")
    print("    GET  /health\n")
    
    print("2️.  Get All Expenses:")
    print("    GET  /expenses\n")
    
    print("="*50)
    print("Test: curl http://localhost:5000/health")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)