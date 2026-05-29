"""
=====================================================
DATABASE CONNECTION MODULE
=====================================================
Purpose: Handles all database connections and query execution
         for the Unitask academic planner application.
Uses: MySQL database via mysql-connector-python package
=====================================================
"""

import mysql.connector
from mysql.connector import Error

# =====================================================
# DATABASE CONFIGURATION
# =====================================================
# Connection settings for MySQL database
DB_CONFIG = {
    'host': 'localhost',          # Database server location (localhost for WAMP)
    'database': 'student_planner', # Database name
    'user': 'root',               # MySQL username
    'password': ''                # MySQL password (empty for default WAMP setup)
                                  # ← CHANGE THIS if you set a password in phpMyAdmin
}

# =====================================================
# CONNECTION FUNCTIONS
# =====================================================
def get_db_connection():
    """
    Establish a connection to the MySQL database.
    
    Returns:
        - mysql.connector.connection: Active database connection if successful
        - None: If connection fails
    """
    try:
        # Create new connection using configuration
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        # Print error message for debugging
        print(f"Database connection error: {e}")
        return None

# =====================================================
# QUERY EXECUTION FUNCTION
# =====================================================
def execute_query(query, params=None, fetch=False):
    """
    Execute a SQL query (SELECT, INSERT, UPDATE, DELETE).
    
    Args:
        query (str): SQL query string with %s placeholders for parameters
        params (tuple/list, optional): Parameters to bind to query
        fetch (bool): If True, return query results; if False, return last row ID
    
    Returns:
        - For SELECT queries (fetch=True): List of dictionaries (rows)
        - For INSERT/UPDATE/DELETE (fetch=False): Last inserted row ID (or True if successful)
        - None/False: If query execution fails
    
    Example:
        # SELECT query
        tasks = execute_query("SELECT * FROM tasks WHERE user_id = %s", (user_id,), fetch=True)
        
        # INSERT query
        new_id = execute_query("INSERT INTO tasks (user_id, title) VALUES (%s, %s)", 
                              (user_id, title), fetch=False)
    """
    # Establish database connection
    connection = get_db_connection()
    if not connection:
        # Return appropriate null value if connection fails
        return None if fetch else False
    
    # Create cursor with dictionary=True to return rows as dictionaries
    # (easier to access columns by name instead of index)
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Execute query with parameters (prevents SQL injection)
        cursor.execute(query, params or ())
        
        if fetch:
            # For SELECT queries: return all results as list of dicts
            result = cursor.fetchall()
            return result
        else:
            # For INSERT/UPDATE/DELETE: commit changes and return last inserted ID
            connection.commit()
            return cursor.lastrowid
    except Error as e:
        # Print error message for debugging
        print(f"Query error: {e}")
        # Return appropriate null value if query fails
        return None if fetch else False
    finally:
        # Always close cursor and connection to prevent resource leaks
        cursor.close()
        connection.close()