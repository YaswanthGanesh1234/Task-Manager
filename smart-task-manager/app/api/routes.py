from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.models import User, Task
from app.extensions import db
from app.tasks.services import create_task, update_task, delete_task, get_tasks_for_user
from app.tasks.analytics import get_analytics_for_user
from app.sockets import broadcast_task_update

api_bp = Blueprint('api', __name__)

@api_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400
        
    user = User(name=data.get('name', ''), email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201

@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'message': 'Login successful', 'access_token': access_token, 'user': user.to_dict()}), 200
        
    return jsonify({'message': 'Invalid credentials'}), 401

@api_bp.route('/logout', methods=['POST'])
@jwt_required()
def api_logout():
    return jsonify({'message': 'Successfully logged out'}), 200

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def api_get_tasks():
    user_id = int(get_jwt_identity())
    tasks = get_tasks_for_user(user_id)
    return jsonify([task.to_dict() for task in tasks]), 200

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def api_get_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    return jsonify(task.to_dict()), 200

@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
def api_create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400
        
    task = create_task(data, user_id)
    broadcast_task_update(user_id, 'created', task.to_dict())
    
    return jsonify(task.to_dict()), 201

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def api_update_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    task = update_task(task_id, data, user_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404
        
    broadcast_task_update(user_id, 'updated', task.to_dict())
        
    return jsonify(task.to_dict()), 200

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def api_delete_task(task_id):
    user_id = int(get_jwt_identity())
    
    if delete_task(task_id, user_id):
        broadcast_task_update(user_id, 'deleted', {'id': task_id})
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    return jsonify({'message': 'Task not found'}), 404

@api_bp.route('/analytics', methods=['GET'])
@jwt_required()
def api_get_analytics():
    user_id = int(get_jwt_identity())
    analytics = get_analytics_for_user(user_id)
    return jsonify(analytics), 200
