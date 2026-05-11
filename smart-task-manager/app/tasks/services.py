from app.models import Task
from app.extensions import db

def create_task(data, user_id):
    new_task = Task(
        title=data.get('title'),
        description=data.get('description', ''),
        priority=data.get('priority', 'Medium'),
        status=data.get('status', 'Pending'),
        user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return new_task

def update_task(task_id, data, user_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return None
        
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'status' in data:
        task.status = data['status']
        
    db.session.commit()
    return task

def delete_task(task_id, user_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return False
        
    db.session.delete(task)
    db.session.commit()
    return True

def get_tasks_for_user(user_id):
    return Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
