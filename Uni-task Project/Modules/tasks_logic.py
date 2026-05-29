from db_conn import execute_query

def get_user_tasks(user_id, status=None, category=None):
    query = "SELECT * FROM tasks WHERE user_id = %s"
    params = [user_id]
    
    if status and status != 'all':
        query += " AND status = %s"
        params.append(status)
    
    if category and category != 'all':
        query += " AND category = %s"
        params.append(category)
    
    query += " ORDER BY deadline ASC"
    
    return execute_query(query, tuple(params), fetch=True)

def create_task(user_id, title, description, category, deadline):
    query = """
        INSERT INTO tasks (user_id, title, description, category, deadline, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')
    """
    result = execute_query(query, (user_id, title, description, category, deadline))
    return result is not False

def update_task_status(task_id, user_id, status):
    query = "UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s"
    result = execute_query(query, (status, task_id, user_id))
    return result is not False

def get_task_summary(user_id):
    tasks = get_user_tasks(user_id)
    total = len(tasks)
    completed = sum(1 for t in tasks if t['status'] == 'completed')
    pending = total - completed
    
    categories = {
        'assignment': 0,
        'exam': 0,
        'lecture': 0,
        'other': 0
    }
    for task in tasks:
        categories[task['category']] += 1
    
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'completion_rate': (completed / total * 100) if total > 0 else 0,
        'categories': categories
    }