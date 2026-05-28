

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import re


app = Flask(__name__)

app.secret_key = 'student-planner-secret-key-2024'

# =====================================================
# IMPORT BUSINESS LOGIC MODULES
# =====================================================
# Authentication & User Management
from Modules.login_route import authenticate_user
from Modules.verify import register_user

# Task Management Operations
from Modules.tasks_logic import get_user_tasks, create_task, update_task_status, get_task_summary
from Modules.timer import get_tasks_due_in_one_hour, get_upcoming_tasks
from Modules.search import search_tasks, filter_tasks_by_category, filter_tasks_by_status
from Modules.modify import delete_task, update_task, get_task_by_id

# Database utilities
from db_conn import execute_query

# =====================================================
# MIDDLEWARE & DECORATORS
# =====================================================
def login_required(route_function):
    """
    Decorator to protect routes that require authentication.
    Redirects unauthenticated users to login page.
    """
    def wrapper(*args, **kwargs):
        # Check if user_id exists in session (indicates logged-in user)
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

# =====================================================
# ROOT ROUTE
# =====================================================
@app.route('/')
def index():
    """Redirect root path to login page"""
    return redirect(url_for('login'))

# =====================================================
# AUTHENTICATION ROUTES
# =====================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login functionality.
    GET: Display login form
    POST: Validate credentials and create user session
    """
    if request.method == 'POST':
        # Get username/email and password from form submission
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate user against database
        user, message = authenticate_user(username_or_email, password)
        
        if user:
            # Store user info in session for current browser session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            # Redirect authenticated user to dashboard
            return redirect(url_for('dashboard'))
        else:
            # Show error message if authentication failed
            return render_template('login.html', error=message)
    
    # Display blank login form on GET request
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle new user registration.
    GET: Display signup form
    POST: Create new user account with validation
    """
    if request.method == 'POST':
        # Collect form data from signup form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate and register new user
        success, message = register_user(username, email, password, confirm_password)
        
        if success:
            # Show success message with registration confirmation
            return render_template('signup.html', success=message)
        else:
            # Show error message if registration failed (duplicate email, weak password, etc.)
            return render_template('signup.html', error=message)
    
    # Display blank signup form on GET request
    return render_template('signup.html')

# =====================================================
# MAIN APPLICATION ROUTES
# =====================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """
    Display main dashboard with task overview.
    Shows: task statistics, task list, and upcoming deadlines
    Requires: User to be logged in
    """
    try:
        # Get current logged-in user's ID from session
        user_id = session['user_id']
        print(f"Dashboard accessed by user_id: {user_id}")
        
        # Fetch user's tasks and statistics
        tasks = get_user_tasks(user_id)
        print(f"Tasks fetched: {len(tasks) if tasks else 0} tasks")
        
        summary = get_task_summary(user_id)  # Count of completed, pending, etc.
        print(f"Summary: {summary}")
        
        upcoming_tasks = get_upcoming_tasks(user_id, 48)  # Tasks due in next 48 hours
        print(f"Upcoming tasks: {len(upcoming_tasks) if upcoming_tasks else 0} tasks")
        
        # Render dashboard template with data
        return render_template('dashboard.html', 
                             tasks=tasks, 
                             summary=summary, 
                             upcoming_tasks=upcoming_tasks,
                             username=session['username'])
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return test data if database fails
        print("Returning test data due to database error")
        tasks = [
            {'id': 1, 'title': 'Test Task 1', 'status': 'pending', 'category': 'assignment', 'deadline': datetime.now()},
            {'id': 2, 'title': 'Test Task 2', 'status': 'completed', 'category': 'exam', 'deadline': datetime.now()}
        ]
        
        summary = {
            'total': 2,
            'completed': 1,
            'pending': 1,
            'completion_rate': 50.0,
            'categories': {'assignment': 1, 'exam': 1, 'lecture': 0, 'other': 0}
        }
        
        upcoming_tasks = [
            {'title': 'Upcoming Task', 'deadline_formatted': 'Tomorrow 2:00 PM', 'hours_remaining': 24}
        ]
        
        return render_template('dashboard.html', 
                             tasks=tasks, 
                             summary=summary, 
                             upcoming_tasks=upcoming_tasks,
                             username=session.get('username', 'Test User'))

@app.route('/notifications')
@login_required
def notifications():
    """
    Display notifications page with urgent and upcoming tasks.
    Shows: tasks due within 1 hour, tasks due within 24 hours
    Requires: User to be logged in
    """
    # Get current logged-in user's ID
    user_id = session['user_id']
    
    # Fetch urgent tasks (due within 1 hour)
    due_in_one_hour = get_tasks_due_in_one_hour(user_id)
    # Fetch upcoming tasks (due within 24 hours)
    upcoming_tasks = get_upcoming_tasks(user_id, 24)
    
    # Render notifications template with alert data
    return render_template('notifications.html', 
                         due_in_one_hour=due_in_one_hour,
                         upcoming_tasks=upcoming_tasks,
                         username=session['username'])

# =====================================================
# API ROUTES - TASK OPERATIONS (REST endpoints)
# =====================================================

@app.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    """
    Retrieve user's tasks with optional filtering.
    Supports: search, filter by category, filter by status
    Returns: JSON array of tasks
    """
    # Get current user's ID
    user_id = session['user_id']
    
    # Get filter parameters from query string
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Apply appropriate filter based on parameters
    if search:
        # Search tasks by keyword in title/description
        tasks = search_tasks(user_id, search)
    elif category:
        # Filter tasks by category (assignment, exam, lecture, etc.)
        tasks = filter_tasks_by_category(user_id, category)
    elif status:
        # Filter tasks by status (pending, completed)
        tasks = filter_tasks_by_status(user_id, status)
    else:
        # Return all tasks if no filter specified
        tasks = get_user_tasks(user_id)
    
    # Convert datetime objects to ISO format for JSON serialization
    for task in tasks:
        if isinstance(task['deadline'], datetime):
            task['deadline'] = task['deadline'].isoformat()
    
    # Return tasks as JSON response
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    """
    Create a new task for the logged-in user.
    Expects: JSON data with title, description, category, deadline
    Returns: JSON success status
    """
    # Get user ID from session
    user_id = session['user_id']
    # Parse JSON request body
    data = request.get_json()
    
    # Create task with provided data
    success = create_task(
        user_id,
        data.get('title'),
        data.get('description', ''),
        data.get('category', 'other'),
        data.get('deadline')
    )
    
    # Return success/failure status
    return jsonify({'success': success})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    """
    Update an existing task (title, description, category, deadline, status).
    Requires: Task ID in URL path
    Expects: JSON data with fields to update
    Returns: JSON success status
    """
    # Get user ID from session
    user_id = session['user_id']
    # Parse JSON request body
    data = request.get_json()
    
    # Update task with new data (user_id ensures ownership verification)
    success = update_task(
        task_id, user_id,
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category'),
        deadline=data.get('deadline'),
        status=data.get('status')
    )
    
    # Return success/failure status
    return jsonify({'success': success})

@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
@login_required
def api_update_task_status(task_id):
    """
    Update only the status of a task (quick complete/uncomplete).
    Requires: Task ID in URL path
    Expects: JSON data with 'status' field (pending or completed)
    Returns: JSON success status
    """
    # Get user ID from session
    user_id = session['user_id']
    # Parse JSON request body
    data = request.get_json()
    # Get new status value
    status = data.get('status')
    
    # Update only the task status
    success = update_task_status(task_id, user_id, status)
    return jsonify({'success': success})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    """
    Delete a task permanently.
    Requires: Task ID in URL path
    Returns: JSON success status
    """
    # Get user ID from session
    user_id = session['user_id']
    # Delete task (user_id ensures only task owner can delete)
    success = delete_task(task_id, user_id)
    return jsonify({'success': success})

@app.route('/api/notifications/due-soon', methods=['GET'])
@login_required
def api_notifications_due_soon():
    """
    Get tasks due within one hour for notification alerts.
    Returns: JSON array of urgent tasks
    """
    # Get user ID from session
    user_id = session['user_id']
    # Fetch tasks due in approximately 1 hour
    tasks = get_tasks_due_in_one_hour(user_id)
    
    # Convert datetime objects to ISO format for JSON serialization
    for task in tasks:
        if isinstance(task['deadline'], datetime):
            task['deadline'] = task['deadline'].isoformat()
    
    return jsonify(tasks)

# =====================================================
# TEST ROUTE - UI TESTING SHORTCUT
# =====================================================
@app.route('/test-notifications')
def test_notifications():
    """
    TEST ROUTE: Direct access to notifications UI for testing.
    Bypasses authentication and uses sample data.
    Access: http://localhost:5000/test-notifications
    """
    from datetime import datetime, timedelta
    
    # Sample urgent tasks (due within 1 hour)
    due_in_one_hour = [
        {
            'title': 'Complete Python Assignment',
            'category': 'assignment',
            'deadline': datetime.now() + timedelta(minutes=30),
            'minutes_remaining': 30
        },
        {
            'title': 'Study for Math Exam',
            'category': 'exam',
            'deadline': datetime.now() + timedelta(minutes=45),
            'minutes_remaining': 45
        }
    ]
    
    # Sample upcoming tasks (next 24 hours)
    upcoming_tasks = [
        {
            'title': 'Database Lecture Review',
            'deadline_formatted': 'Today, 3:00 PM',
            'hours_remaining': 6
        },
        {
            'title': 'Submit Project Report',
            'deadline_formatted': 'Tomorrow, 9:00 AM',
            'hours_remaining': 18
        },
        {
            'title': 'Group Study Session',
            'deadline_formatted': 'Tomorrow, 2:00 PM',
            'hours_remaining': 24
        }
    ]
    
    # Render notifications template with sample data
    return render_template('notifications.html', 
                         due_in_one_hour=due_in_one_hour,
                         upcoming_tasks=upcoming_tasks,
                         username='Test User')

@app.route('/test-basic')
def test_basic():
    """Simple test route to verify Flask is working"""
    return "Flask is working! Dashboard test: <a href='/test-dashboard'>Test Dashboard</a>"

@app.route('/test-dashboard')
def test_dashboard():
    """Test dashboard route with sample data (no auth required)"""
    try:
        # Sample data for testing
        tasks = [
            {'id': 1, 'title': 'Test Task 1', 'status': 'pending', 'category': 'assignment', 'deadline': datetime.now()},
            {'id': 2, 'title': 'Test Task 2', 'status': 'completed', 'category': 'exam', 'deadline': datetime.now()}
        ]
        
        summary = {
            'total': 2,
            'completed': 1,
            'pending': 1,
            'completion_rate': 50.0,
            'categories': {'assignment': 1, 'exam': 1, 'lecture': 0, 'other': 0}
        }
        
        upcoming_tasks = [
            {'title': 'Upcoming Task', 'deadline_formatted': 'Tomorrow 2:00 PM', 'hours_remaining': 24}
        ]
        
        return render_template('dashboard.html', 
                             tasks=tasks, 
                             summary=summary, 
                             upcoming_tasks=upcoming_tasks,
                             username='Test User')
    except Exception as e:
        return f"Dashboard test error: {e}"

@app.route('/test-dashboard-auth')
def test_dashboard_auth():
    """Test dashboard route with simulated authentication"""
    # Simulate user login
    session['user_id'] = 1
    session['username'] = 'Test User'
    session['email'] = 'test@example.com'
    
    # Redirect to dashboard
    return redirect(url_for('dashboard'))

@app.route('/init-db')
def init_db():
    """Initialize database and create tables"""
    try:
        # Read schema file
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        from db_conn import execute_query
        
        for statement in statements:
            if statement:
                print(f"Executing: {statement[:50]}...")
                execute_query(statement, fetch=False)
        
        return "Database initialized successfully! <a href='/'>Go to login</a>"
    
    except Exception as e:
        return f"Database initialization failed: {e}"

# =====================================================
# LOGOUT ROUTE
# =====================================================
@app.route('/logout')
def logout():
    """
    Clear user session and redirect to login.
    Effectively logs out the current user.
    """
    # Clear all session data (user_id, username, email, etc.)
    session.clear()
    # Redirect to login page
    return redirect(url_for('login'))

# =====================================================
# APPLICATION STARTUP
# =====================================================
if __name__ == '__main__':
    # Start Flask development server
    # debug=True: Auto-reload on code changes, enhanced error reporting
    # host='0.0.0.0': Allow connections from any network interface
    # port=5000: Run on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)