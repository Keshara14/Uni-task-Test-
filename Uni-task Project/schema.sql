-- Student Academic Planner Database Schema

CREATE DATABASE IF NOT EXISTS student_planner;
USE student_planner;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    category ENUM('assignment', 'exam', 'lecture', 'other') DEFAULT 'assignment',
    deadline DATETIME NOT NULL,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sample data
INSERT INTO users (username, email, password_hash) VALUES 
('testuser', 'test@example.com', '$2b$12$testhash123');

INSERT INTO tasks (user_id, title, description, category, deadline, status) VALUES
(1, 'Complete Python Project', 'Build the student planner app', 'assignment', DATE_ADD(NOW(), INTERVAL 2 DAY), 'pending'),
(1, 'Midterm Exam', 'Study chapters 1-5', 'exam', DATE_ADD(NOW(), INTERVAL 5 DAY), 'pending'),
(1, 'Database Lecture', 'Watch MySQL tutorial', 'lecture', DATE_ADD(NOW(), INTERVAL 1 DAY), 'completed');