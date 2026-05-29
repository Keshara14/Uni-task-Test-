from db_conn import execute_query

def search_tasks(user_id, search_term):
    query = """
        SELECT * FROM tasks 
        WHERE user_id = %s 
        AND (title LIKE %s OR description LIKE %s)
        ORDER BY deadline ASC
    """
    search_pattern = f"%{search_term}%"
    return execute_query(query, (user_id, search_pattern, search_pattern), fetch=True)

def filter_tasks_by_category(user_id, category):
    if category == 'all':
        query = "SELECT * FROM tasks WHERE user_id = %s ORDER BY deadline ASC"
        params = (user_id,)
    else:
        query = "SELECT * FROM tasks WHERE user_id = %s AND category = %s ORDER BY deadline ASC"
        params = (user_id, category)
    
    return execute_query(query, params, fetch=True)

def filter_tasks_by_status(user_id, status):
    if status == 'all':
        query = "SELECT * FROM tasks WHERE user_id = %s ORDER BY deadline ASC"
        params = (user_id,)
    else:
        query = "SELECT * FROM tasks WHERE user_id = %s AND status = %s ORDER BY deadline ASC"
        params = (user_id, status)
    
    return execute_query(query, params, fetch=True)