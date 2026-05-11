// Global variables
let allTasks = [];
const socket = io();

// Ensure headers for JWT auth
const fetchOptions = {
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${JWT_TOKEN}`
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Setup Socket.IO connection
    socket.on('connect', () => {
        socket.emit('join', { token: JWT_TOKEN });
    });

    socket.on('notification', (data) => {
        showToast(data.message, 'success');
    });

    socket.on('task_update', (data) => {
        if (data.action === 'created' || data.action === 'updated' || data.action === 'deleted') {
            // Re-fetch all tasks to ensure sync and update analytics
            fetchTasks();
        }
    });

    // Event listeners
    document.getElementById('searchInput').addEventListener('input', renderTasks);
    document.getElementById('statusFilter').addEventListener('change', renderTasks);

    // Initial fetch
    fetchTasks();
});

async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks', fetchOptions);
        if (response.ok) {
            allTasks = await response.json();
            document.getElementById('loadingTasksMsg').classList.add('d-none');
            renderTasks();
            updateAnalytics();
        } else {
            showToast('Failed to load tasks', 'danger');
        }
    } catch (error) {
        console.error('Error fetching tasks:', error);
        showToast('Network error', 'danger');
    }
}

async function updateAnalytics() {
    try {
        const response = await fetch('/api/analytics', fetchOptions);
        if (response.ok) {
            const data = await response.json();
            
            // Animate number change (simple version)
            document.getElementById('stat-total').innerText = data.total_tasks;
            document.getElementById('stat-completed').innerText = data.completed_tasks;
            document.getElementById('stat-pending').innerText = data.pending_tasks;
            
            document.getElementById('stat-percent').innerText = `${data.completion_percentage}%`;
            document.getElementById('stat-progress-bar').style.width = `${data.completion_percentage}%`;
        }
    } catch (error) {
        console.error('Error fetching analytics:', error);
    }
}

function renderTasks() {
    const tbody = document.getElementById('taskTableBody');
    const noTasksMsg = document.getElementById('noTasksMsg');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;

    tbody.innerHTML = '';

    const filteredTasks = allTasks.filter(task => {
        const matchesSearch = task.title.toLowerCase().includes(searchTerm) || 
                              (task.description && task.description.toLowerCase().includes(searchTerm));
        const matchesStatus = statusFilter === 'All' || task.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    if (filteredTasks.length === 0) {
        noTasksMsg.classList.remove('d-none');
    } else {
        noTasksMsg.classList.add('d-none');
        
        filteredTasks.forEach(task => {
            const tr = document.createElement('tr');
            
            // Format date
            const createdDate = new Date(task.created_at).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric'
            });

            tr.innerHTML = `
                <td class="fw-medium">${task.title}</td>
                <td class="text-truncate" style="max-width: 200px;">${task.description || '<span class="text-muted-light">No description</span>'}</td>
                <td><span class="badge badge-priority-${task.priority.toLowerCase()} rounded-pill px-3">${task.priority}</span></td>
                <td><span class="badge badge-status-${task.status.toLowerCase().replace(' ', '-')} rounded-pill px-3">${task.status}</span></td>
                <td class="text-muted-light">${createdDate}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1 border-0" onclick="prepareEditModal(${task.id})" title="Edit">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger border-0" onclick="showDeleteModal(${task.id})" title="Delete">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function prepareAddModal() {
    document.getElementById('taskForm').reset();
    document.getElementById('taskId').value = '';
    document.getElementById('taskModalLabel').innerText = 'Add Task';
}

function prepareEditModal(id) {
    const task = allTasks.find(t => t.id === id);
    if (!task) return;

    document.getElementById('taskId').value = task.id;
    document.getElementById('taskTitle').value = task.title;
    document.getElementById('taskDescription').value = task.description || '';
    document.getElementById('taskPriority').value = task.priority;
    document.getElementById('taskStatus').value = task.status;
    
    document.getElementById('taskModalLabel').innerText = 'Edit Task';
    
    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

async function saveTask() {
    const id = document.getElementById('taskId').value;
    const title = document.getElementById('taskTitle').value;
    
    if (!title) {
        showToast('Title is required', 'warning');
        return;
    }

    const taskData = {
        title: title,
        description: document.getElementById('taskDescription').value,
        priority: document.getElementById('taskPriority').value,
        status: document.getElementById('taskStatus').value
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/tasks/${id}` : '/api/tasks';

    // Disable button to prevent double clicks
    const btn = document.getElementById('saveTaskBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    btn.disabled = true;

    try {
        const response = await fetch(url, {
            ...fetchOptions,
            method: method,
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            showToast(`Task ${id ? 'updated' : 'added'} successfully`, 'success');
            // Hide modal
            const modalEl = document.getElementById('taskModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            // Data will be re-fetched via Socket.IO broadcast, but we can also manually call it just in case
            fetchTasks();
        } else {
            const err = await response.json();
            showToast(err.message || 'Error saving task', 'danger');
        }
    } catch (error) {
        console.error('Save error:', error);
        showToast('Network error while saving', 'danger');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function showDeleteModal(id) {
    document.getElementById('deleteTaskId').value = id;
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

async function confirmDeleteTask() {
    const id = document.getElementById('deleteTaskId').value;
    if (!id) return;

    try {
        const response = await fetch(`/api/tasks/${id}`, {
            ...fetchOptions,
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Task deleted successfully', 'success');
            const modalEl = document.getElementById('deleteModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            fetchTasks();
        } else {
            showToast('Error deleting task', 'danger');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Network error while deleting', 'danger');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('js-toast-container');
    const id = 'toast-' + Math.random().toString(36).substr(2, 9);
    
    // Map type to Bootstrap background colors
    let bgClass = 'text-bg-primary';
    if (type === 'success') bgClass = 'text-bg-success';
    if (type === 'danger') bgClass = 'text-bg-danger';
    if (type === 'warning') bgClass = 'text-bg-warning text-dark';
    if (type === 'info') bgClass = 'text-bg-info text-dark';

    const toastHTML = `
        <div id="${id}" class="toast align-items-center ${bgClass} border-0 glass-toast mt-2" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body fw-medium">
                    ${message}
                </div>
                <button type="button" class="btn-close ${type !== 'warning' && type !== 'info' ? 'btn-close-white' : ''} me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(id);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}
