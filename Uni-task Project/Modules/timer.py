from datetime import datetime, timedelta
from db_conn import execute_query

def get_tasks_due_in_one_hour(user_id):
    now = datetime.now()
    target_time = now + timedelta(hours=1)
    
    query = """
        SELECT * FROM tasks 
        WHERE user_id = %s 
        AND status = 'pending'
        AND deadline BETWEEN %s AND %s
        ORDER BY deadline ASC
    """
    
    tasks = execute_query(query, (user_id, now, target_time), fetch=True)
    
    for task in tasks:
        if isinstance(task['deadline'], datetime):
            remaining = task['deadline'] - now
            task['minutes_remaining'] = int(remaining.total_seconds() / 60)
            task['hours_remaining'] = round(remaining.total_seconds() / 3600, 1)
    
    return tasks or []

def get_upcoming_tasks(user_id, hours=24):
    now = datetime.now()
    future = now + timedelta(hours=hours)
    
    query = """
        SELECT * FROM tasks 
        WHERE user_id = %s 
        AND status = 'pending'
        AND deadline BETWEEN %s AND %s
        ORDER BY deadline ASC
    """
    
    tasks = execute_query(query, (user_id, now, future), fetch=True)
    
    for task in tasks:
        if isinstance(task['deadline'], datetime):
            task['deadline_formatted'] = task['deadline'].strftime("%B %d, %I:%M %p")
            remaining = task['deadline'] - now
            task['hours_remaining'] = round(remaining.total_seconds() / 3600, 1)
    
    return tasks or []