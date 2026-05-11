import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Use eventlet or gevent for production, standard werkzeug for dev
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
