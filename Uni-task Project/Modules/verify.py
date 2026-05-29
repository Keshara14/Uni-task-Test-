from Modules.hash import hash_password, validate_email, validate_password_strength
from db_conn import execute_query

def register_user(username, email, password, confirm_password):
    if password != confirm_password:
        return False, "Passwords do not match"
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    is_strong, message = validate_password_strength(password)
    if not is_strong:
        return False, message
    
    check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
    existing = execute_query(check_query, (username, email), fetch=True)
    
    if existing:
        if existing[0]['username'] == username:
            return False, "Username already taken"
        return False, "Email already registered"
    
    hashed_password = hash_password(password)
    insert_query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
    result = execute_query(insert_query, (username, email, hashed_password))
    
    if result:
        return True, "Registration successful! Please login."
    return False, "Registration failed. Please try again."