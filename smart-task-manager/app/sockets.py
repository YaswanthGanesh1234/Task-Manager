from app.extensions import socketio
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('join')
def handle_join(data):
    token = data.get('token')
    if token:
        try:
            decoded = decode_token(token)
            user_id = str(decoded['sub'])
            join_room(user_id)
            emit('notification', {'message': 'Connected to real-time updates'}, room=user_id)
        except Exception as e:
            print(f"Socket join error: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    pass

def broadcast_task_update(user_id, action, task_data):
    """
    Broadcasts task changes to the specific user's room.
    Action can be 'created', 'updated', or 'deleted'.
    """
    socketio.emit('task_update', {
        'action': action,
        'task': task_data
    }, room=str(user_id))
