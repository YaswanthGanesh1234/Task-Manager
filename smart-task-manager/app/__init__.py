from flask import Flask
from app.config import config_by_name
from app.extensions import db, login_manager, jwt, socketio, cors

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        # User loader for Flask-Login
        from app.models import User
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Register Blueprints
        from app.auth.routes import auth_bp
        from app.tasks.routes import tasks_bp
        from app.api.routes import api_bp

        app.register_blueprint(auth_bp, url_prefix='/')
        app.register_blueprint(tasks_bp, url_prefix='/')
        app.register_blueprint(api_bp, url_prefix='/api')

        # Import sockets
        import app.sockets

        # Ensure database tables exist (useful for dev)
        db.create_all()

    return app
