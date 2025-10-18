import jwt
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User
from app.extensions import db

def token_required(f):
    """Decorator to protect routes by requiring a valid JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Use modern db.session.get() instead of legacy User.query.get()
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                 return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # The 'current_user' is passed directly from the 'token_required' decorator
        if not current_user.role or current_user.role != 'admin':
            return jsonify({'message': 'Admin privilege required!'}), 403
        
        # Pass the current_user object to the decorated function (e.g., the route)
        return f(current_user, *args, **kwargs)
    return decorated

