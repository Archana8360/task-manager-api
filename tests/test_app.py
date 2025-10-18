import sys
import os
import pytest
import json

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from config import TestingConfig

# Changed scope to 'function' to ensure a fresh database for every test
@pytest.fixture(scope='function')
def test_client():
    """Create a test client for the Flask application for each test."""
    app = create_app(config_class=TestingConfig)
    
    with app.app_context():
        db.create_all()
        with app.test_client() as testing_client:
            yield testing_client
        db.drop_all()

# Changed scope to 'function' to align with the test_client fixture
@pytest.fixture(scope='function')
def auth_tokens(test_client):
    """Fixture to register and log in an admin and a regular user for each test."""
    tokens = {}
    
    # Register and log in the first user (becomes admin)
    test_client.post('/auth/register', json={'username': 'adminuser', 'password': 'adminpassword'})
    res = test_client.post('/auth/login', json={'username': 'adminuser', 'password': 'adminpassword'})
    tokens['admin'] = json.loads(res.data)['token']

    # Register and log in a second user (regular user)
    test_client.post('/auth/register', json={'username': 'testuser', 'password': 'testpassword'})
    res = test_client.post('/auth/login', json={'username': 'testuser', 'password': 'testpassword'})
    tokens['user'] = json.loads(res.data)['token']
    
    return tokens

### Authentication Tests ###

def test_user_registration(test_client):
    """Test user registration."""
    response = test_client.post('/auth/register', json={'username': 'newuser', 'password': 'newpassword'})
    assert response.status_code == 201
    assert b'User registered successfully' in response.data

def test_duplicate_user_registration(test_client):
    """Test that registering a user with an existing username fails."""
    test_client.post('/auth/register', json={'username': 'dupuser', 'password': 'password'})
    response = test_client.post('/auth/register', json={'username': 'dupuser', 'password': 'password'})
    assert response.status_code == 409

def test_user_login(test_client):
    """Test user login and token generation."""
    test_client.post('/auth/register', json={'username': 'loginuser', 'password': 'loginpassword'})
    response = test_client.post('/auth/login', json={'username': 'loginuser', 'password': 'loginpassword'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_invalid_login(test_client):
    """Test login with incorrect credentials."""
    response = test_client.post('/auth/login', json={'username': 'nouser', 'password': 'wrongpassword'})
    assert response.status_code == 401

### Task Endpoint Tests ###

def test_create_task(test_client, auth_tokens):
    """Test creating a new task with a valid token."""
    response = test_client.post('/tasks',
        headers={'x-access-token': auth_tokens['user']},
        json={'title': 'Test Task 1', 'description': 'This is a test.'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Task 1'

def test_create_task_unauthorized(test_client):
    """Test that creating a task without a token fails."""
    response = test_client.post('/tasks', json={'title': 'Unauthorized Task'})
    assert response.status_code == 401

def test_get_tasks(test_client, auth_tokens):
    """Test retrieving tasks for the logged-in user."""
    response = test_client.get('/tasks', headers={'x-access-token': auth_tokens['user']})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data['tasks'], list)

def test_get_tasks_pagination_and_filtering(test_client, auth_tokens):
    """Test pagination and filtering of tasks."""
    test_client.post('/tasks', headers={'x-access-token': auth_tokens['user']}, json={'title': 'Task A', 'completed': False})
    test_client.post('/tasks', headers={'x-access-token': auth_tokens['user']}, json={'title': 'Task B', 'completed': True})
    
    response = test_client.get('/tasks?completed=true', headers={'x-access-token': auth_tokens['user']})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['tasks']) == 1
    assert data['tasks'][0]['completed'] is True
    
    response = test_client.get('/tasks?page=1&per_page=1', headers={'x-access-token': auth_tokens['user']})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['tasks']) == 1

def test_update_task(test_client, auth_tokens):
    """Test updating an existing task."""
    res = test_client.post('/tasks', headers={'x-access-token': auth_tokens['user']}, json={'title': 'To Be Updated'})
    task_id = json.loads(res.data)['id']
    
    response = test_client.put(f'/tasks/{task_id}',
        headers={'x-access-token': auth_tokens['user']},
        json={'title': 'Updated Title', 'completed': True}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated Title'

def test_delete_task(test_client, auth_tokens):
    """Test deleting a task."""
    res = test_client.post('/tasks', headers={'x-access-token': auth_tokens['user']}, json={'title': 'To Be Deleted'})
    task_id = json.loads(res.data)['id']
    
    response = test_client.delete(f'/tasks/{task_id}', headers={'x-access-token': auth_tokens['user']})
    assert response.status_code == 200
    assert b'Task deleted successfully' in response.data

### Role-Based Authorization Tests ###

def test_admin_can_access_admin_route(test_client, auth_tokens):
    """Test that an admin user can access the admin-only route."""
    response = test_client.get('/admin/tasks/all', headers={'x-access-token': auth_tokens['admin']})
    assert response.status_code == 200

def test_user_cannot_access_admin_route(test_client, auth_tokens):
    """Test that a regular user is forbidden from accessing the admin-only route."""
    response = test_client.get('/admin/tasks/all', headers={'x-access-token': auth_tokens['user']})
    assert response.status_code == 403

