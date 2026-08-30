import sqlite3
import os
from typing import List, Dict, Any
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "scm.db")

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE,
            category TEXT,
            unit_cost REAL,
            supplier_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create suppliers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_email TEXT,
            phone TEXT,
            address TEXT,
            rating REAL DEFAULT 5.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create inventory_transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            transaction_type TEXT, -- 'in', 'out', 'adjustment'
            quantity INTEGER,
            unit_cost REAL,
            total_value REAL,
            reference TEXT, -- PO number, SO number, etc.
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Create forecast_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecast_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            forecast_date DATE,
            forecasted_quantity REAL,
            confidence_lower REAL,
            confidence_upper REAL,
            model_used TEXT,
            accuracy_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # Create risk_assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            supplier_id INTEGER,
            risk_type TEXT, -- 'stockout', 'supplier', 'demand'
            risk_score REAL,
            risk_level TEXT, -- 'low', 'medium', 'high', 'critical'
            recommendations TEXT,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')

    conn.commit()
    conn.close()

def get_inventory_summary() -> Dict[str, Any]:
    """Get inventory summary statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Get total suppliers
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    total_suppliers = cursor.fetchone()[0]

    # Get inventory value
    cursor.execute("""
        SELECT SUM(quantity * unit_cost)
        FROM inventory_transactions
        WHERE transaction_type = 'in'
    """)
    inventory_value = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "inventory_value": inventory_value,
        "last_updated": pd.Timestamp.now().isoformat()
    }

def save_forecast_result(product_id: int, forecast_data: Dict[str, Any]):
    """Save forecast result to database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO forecast_results
        (product_id, forecast_date, forecasted_quantity, confidence_lower,
         confidence_upper, model_used, accuracy_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        product_id,
        forecast_data['date'],
        forecast_data['quantity'],
        forecast_data.get('confidence_lower'),
        forecast_data.get('confidence_upper'),
        forecast_data.get('model', 'unknown'),
        forecast_data.get('accuracy')
    ))

    conn.commit()
    conn.close()

def get_recent_forecasts(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent forecast results"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fr.*, p.name as product_name
        FROM forecast_results fr
        JOIN products p ON fr.product_id = p.id
        ORDER BY fr.created_at DESC
        LIMIT ?
    """, (limit,))

    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return results