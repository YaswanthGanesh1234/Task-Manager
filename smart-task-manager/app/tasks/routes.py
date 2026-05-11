from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask_jwt_extended import create_access_token

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def dashboard():
    # Generate a JWT token so the frontend JS can authenticate with the API
    access_token = create_access_token(identity=current_user.id)
    return render_template('dashboard.html', user=current_user, jwt_token=access_token)
