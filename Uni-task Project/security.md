# Security Documentation - Student Academic Planner

## Password Security Implementation

### Hashing Algorithm
- **Algorithm**: bcrypt
- **Salt Rounds**: 12
- **Library**: bcrypt Python library

### How Password Hashing Works

1. When a user signs up:
   - Password is received from the form
   - A random salt is generated (12 rounds)
   - Password + salt are hashed together
   - Only the hash is stored in the database

2. When a user logs in:
   - Entered password is hashed with the stored salt
   - Compared to the stored hash
   - Original password is never stored anywhere

### Example Hash Output


### Password Requirements
- Minimum 6 characters
- At least 1 uppercase letter
- At least 1 number

### Security Best Practices Implemented

1. **No plaintext passwords stored**
2. **Unique salt per password**
3. **SQL injection prevention** (parameterized queries)
4. **Session management** with Flask sessions
5. **Login required decorator** for protected routes

### File Reference
- `modules/hash.py` - Contains hashing functions
- `modules/verify.py` - Contains password validation

### Never Commit to Repository
- Database credentials
- Secret keys
- Actual password hashes from production