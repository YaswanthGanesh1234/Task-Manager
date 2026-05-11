import pandas as pd
import numpy as np
from app.models import Task

def get_analytics_for_user(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    if not tasks:
        return {
            'total_tasks': 0,
            'completed_tasks': 0,
            'pending_tasks': 0,
            'in_progress_tasks': 0,
            'completion_percentage': 0,
            'high_priority_count': 0,
            'status_distribution': {'Pending': 0, 'In Progress': 0, 'Completed': 0},
            'priority_distribution': {'Low': 0, 'Medium': 0, 'High': 0}
        }
        
    # Convert to pandas DataFrame
    df = pd.DataFrame([{
        'id': t.id,
        'title': t.title,
        'priority': t.priority,
        'status': t.status
    } for t in tasks])
    
    # Use NumPy & Pandas for analytics
    total_tasks = len(df)
    completed_tasks = int(np.sum(df['status'] == 'Completed'))
    pending_tasks = int(np.sum(df['status'] == 'Pending'))
    in_progress_tasks = int(np.sum(df['status'] == 'In Progress'))
    
    completion_percentage = float(np.round((completed_tasks / total_tasks) * 100, 2)) if total_tasks > 0 else 0.0
    high_priority_count = int(np.sum(df['priority'] == 'High'))
    
    status_distribution = df['status'].value_counts().to_dict()
    priority_distribution = df['priority'].value_counts().to_dict()
    
    # Ensure all keys exist
    for stat in ['Pending', 'In Progress', 'Completed']:
        if stat not in status_distribution:
            status_distribution[stat] = 0
            
    for prio in ['Low', 'Medium', 'High']:
        if prio not in priority_distribution:
            priority_distribution[prio] = 0
            
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_percentage': completion_percentage,
        'high_priority_count': high_priority_count,
        'status_distribution': status_distribution,
        'priority_distribution': priority_distribution
    }
