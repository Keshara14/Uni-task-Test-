from Modules.hash import verify_password
from db_conn import execute_query

def authenticate_user(username_or_email, password):
    query = """
        SELECT id, username, email, password_hash 
        FROM users 
        WHERE username = %s OR email = %s
    """
    user = execute_query(query, (username_or_email, username_or_email), fetch=True)
    
    if not user:
        return None, "User not found"
    
    user = user[0]
    
    if verify_password(password, user['password_hash']):
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }, "Login successful"
    else:
        return None, "Invalid password"