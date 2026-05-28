from db_conn import execute_query

def delete_task(task_id, user_id):
    query = "DELETE FROM tasks WHERE id = %s AND user_id = %s"
    result = execute_query(query, (task_id, user_id))
    return result is not False

def update_task(task_id, user_id, title=None, description=None, category=None, deadline=None, status=None):
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = %s")
        params.append(title)
    if description is not None:
        updates.append("description = %s")
        params.append(description)
    if category is not None:
        updates.append("category = %s")
        params.append(category)
    if deadline is not None:
        updates.append("deadline = %s")
        params.append(deadline)
    if status is not None:
        updates.append("status = %s")
        params.append(status)
    
    if not updates:
        return False
    
    params.extend([task_id, user_id])
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
    result = execute_query(query, tuple(params))
    return result is not False

def get_task_by_id(task_id, user_id):
    query = "SELECT * FROM tasks WHERE id = %s AND user_id = %s"
    result = execute_query(query, (task_id, user_id), fetch=True)
    return result[0] if result else None