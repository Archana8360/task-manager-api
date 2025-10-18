from flask import Blueprint, request, jsonify, current_app
from app.models import User
from app.extensions import db
import jwt
from datetime import datetime, timedelta, UTC

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint. The first user to register becomes an admin.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          $ref: '#/definitions/UserRegistration'
        required: true
        description: User registration details
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing username or password
      409:
        description: Username already exists
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required!'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 409

    # Determine role: first user is admin, others are regular users
    role = 'admin' if not User.query.first() else 'user'

    new_user = User(username=data['username'], role=role)
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

@auth.route('/login', methods=['POST'])
def login():
    """
    User login endpoint. Returns a JWT on successful authentication.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          $ref: '#/definitions/UserLogin'
        required: true
        description: User login credentials
    responses:
      200:
        description: Login successful, returns auth token
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Could not verify'}), 401

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password!'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(UTC) + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

