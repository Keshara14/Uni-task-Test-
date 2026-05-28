/* ========================================
   ACTIONS.JS - All Interactive JavaScript
   Member 08: Thilina (Action Dev)
   
   This file contains ALL JavaScript functionality:
   - Edit/Delete operations
   - Task status toggle
   - Filter and search
   - Modal handling
   - Toast notifications
   ======================================== */

// Make functions available globally
window.toggleStatus = toggleStatus;
window.deleteTask = deleteTask;
window.editTask = editTask;
window.showAddTaskModal = showAddTaskModal;
window.closeModal = closeModal;
window.filterTasks = filterTasks;
window.searchTasks = searchTasks;

// Global variables
let currentEditTaskId = null;

// ========================================
// TASK STATUS TOGGLE (Complete/Incomplete)
// ========================================

async function toggleStatus(taskId, isChecked) {
    const status = isChecked ? 'completed' : 'pending';
    
    try {
        const response = await fetch(`/api/tasks/${taskId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: status })
        });
        
        if (response.ok) {
            // Update the UI without reload
            const taskCard = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                if (status === 'completed') {
                    taskCard.classList.add('completed-task');
                } else {
                    taskCard.classList.remove('completed-task');
                }
            }
            
            // Show success notification
            showToast('Task status updated!', 'success');
            
            // Refresh after 1 second to update summary stats
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to update status', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    }
}

// ========================================
// DELETE TASK FUNCTION
// ========================================

async function deleteTask(taskId) {
    // Confirmation dialog
    const confirmed = confirm('⚠️ Are you sure you want to delete this task?\n\nThis action cannot be undone!');
    
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Animate removal
            const taskCard = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
            if (taskCard) {
                taskCard.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => {
                    taskCard.remove();
                    showToast('Task deleted successfully!', 'success');
                    // Reload to update summary stats
                    setTimeout(() => location.reload(), 500);
                }, 300);
            } else {
                location.reload();
            }
        } else {
            showToast('Failed to delete task', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    }
}

// ========================================
// EDIT TASK FUNCTION
// ========================================

async function editTask(taskId) {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        const task = tasks.find(t => t.id === taskId);
        
        if (task) {
            currentEditTaskId = taskId;
            document.getElementById('modalTitle').textContent = 'Edit Task';
            document.getElementById('taskId').value = task.id;
            document.getElementById('taskTitle').value = task.title;
            document.getElementById('taskDescription').value = task.description || '';
            document.getElementById('taskCategory').value = task.category;
            
            // Format datetime-local input
            const deadline = new Date(task.deadline);
            const formattedDeadline = deadline.toISOString().slice(0, 16);
            document.getElementById('taskDeadline').value = formattedDeadline;
            
            document.getElementById('taskModal').style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to load task data', 'error');
    }
}

// ========================================
// ADD TASK MODAL
// ========================================

function showAddTaskModal() {
    currentEditTaskId = null;
    document.getElementById('modalTitle').textContent = 'Add New Task';
    document.getElementById('taskForm').reset();
    document.getElementById('taskId').value = '';
    document.getElementById('taskModal').classList.add('show');
}

function closeModal() {
    document.getElementById('taskModal').classList.remove('show');
}

// ========================================
// SAVE TASK (Create or Update)
// ========================================

document.getElementById('taskForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const taskId = document.getElementById('taskId').value;
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        category: document.getElementById('taskCategory').value,
        deadline: document.getElementById('taskDeadline').value
    };
    
    try {
        let response;
        
        if (taskId) {
            // Update existing task
            response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        } else {
            // Create new task
            response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        }
        
        if (response.ok) {
            showToast(taskId ? 'Task updated!' : 'Task created!', 'success');
            closeModal();
            setTimeout(() => location.reload(), 500);
        } else {
            showToast('Failed to save task', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
    }
});

// ========================================
// FILTER AND SEARCH FUNCTIONS
// ========================================

async function filterTasks() {
    const category = document.getElementById('categoryFilter')?.value || 'all';
    const status = document.getElementById('statusFilter')?.value || 'all';
    let url = '/api/tasks?';
    
    if (category !== 'all') {
        url += `category=${category}`;
    } else if (status !== 'all') {
        url += `status=${status}`;
    } else {
        url = '/api/tasks';
    }
    
    try {
        const response = await fetch(url);
        const tasks = await response.json();
        renderTaskCards(tasks);
    } catch (error) {
        console.error('Error:', error);
    }
}

async function searchTasks() {
    const searchTerm = document.getElementById('searchInput')?.value;
    if (!searchTerm || searchTerm.length < 2) {
        if (searchTerm.length === 0) filterTasks();
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks?search=${encodeURIComponent(searchTerm)}`);
        const tasks = await response.json();
        renderTaskCards(tasks);
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========================================
// RENDER TASK CARDS DYNAMICALLY
// ========================================

function renderTaskCards(tasks) {
    const grid = document.getElementById('tasksGrid');
    if (!grid) return;
    
    if (tasks.length === 0) {
        grid.innerHTML = '<div class="no-tasks">No tasks found <i class="fas fa-smile-wink"></i></div>';
        return;
    }
    
    grid.innerHTML = tasks.map(task => `
        <div class="task-card ${task.status === 'completed' ? 'completed-task' : ''}" data-task-id="${task.id}">
            <div class="task-header">
                <span class="task-category category-${task.category}">
                    ${getCategoryIcon(task.category)} ${capitalize(task.category)}
                </span>
                <div class="task-actions">
                    <button class="edit-btn" onclick="window.editTask(${task.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-btn" onclick="window.deleteTask(${task.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <h3>${escapeHtml(task.title)}</h3>
            <p>${escapeHtml(task.description || 'No description')}</p>
            <div class="task-footer">
                <div class="deadline">
                    <i class="fas fa-calendar-alt"></i>
                    <span>${formatDate(task.deadline)}</span>
                </div>
                <label class="checkbox-label">
                    <input type="checkbox" ${task.status === 'completed' ? 'checked' : ''} 
                           onchange="window.toggleStatus(${task.id}, this.checked)">
                    <span>Complete</span>
                </label>
            </div>
        </div>
    `).join('');
}

// ========================================
// HELPER FUNCTIONS
// ========================================

function getCategoryIcon(category) {
    const icons = {
        'assignment': '📝',
        'exam': '📚',
        'lecture': '🎓',
        'other': '📌'
    };
    return icons[category] || '📌';
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function showToast(message, type) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Style the toast
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : '#f44336'};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    document.body.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('taskModal');
    if (event.target === modal) {
        closeModal();
    }
}

// ========================================
// SCROLL REVEAL EFFECT (Creative Scroll Animation)
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    // Select elements we want to reveal on scroll
    const revealElements = document.querySelectorAll(
        '.stat-card, .card, .breakdown-box, .upcoming-task-item, .task-card'
    );
    
    // Add scroll reveal base classes dynamically and set stagger delay
    revealElements.forEach((el, index) => {
        el.classList.add('scroll-reveal-item');
        
        // Calculate dynamic stagger delay based on relative index
        const delay = (index % 4) * 100; // stagger up to 300ms
        el.style.setProperty('--reveal-delay', `${delay}ms`);
    });

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                // Once it has animated, stop observing for hardware optimization
                observer.unobserve(entry.target);
            }
        });
    }, {
        root: null, // viewport
        threshold: 0.05, // trigger when 5% of the element is visible
        rootMargin: '0px 0px -20px 0px' // offset trigger before entering viewport
    });

    revealElements.forEach(el => revealObserver.observe(el));
});