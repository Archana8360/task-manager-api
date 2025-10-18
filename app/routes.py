from flask import Blueprint, request, jsonify
from app.models import Task
from app.extensions import db
from app.decorators import token_required, admin_required

main = Blueprint('main', __name__)

@main.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    """
    Retrieve all tasks for the logged-in user.
    ---
    tags:
      - Tasks
    security:
      - ApiKeyAuth: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: The page number for pagination.
      - in: query
        name: per_page
        type: integer
        default: 10
        description: The number of tasks per page.
      - in: query
        name: completed
        type: boolean
        description: Filter tasks by their completion status (true/false).
    responses:
      200:
        description: A list of tasks with pagination details.
        schema:
          type: object
          properties:
            tasks:
              type: array
              items:
                $ref: '#/definitions/Task'
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Task.query.filter_by(user_id=current_user.id)

    if 'completed' in request.args:
        completed_filter = request.args.get('completed', type=str).lower() == 'true'
        query = query.filter_by(completed=completed_filter)

    paginated_tasks = query.paginate(page=page, per_page=per_page, error_out=False)
    tasks = paginated_tasks.items
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks],
        'total': paginated_tasks.total,
        'pages': paginated_tasks.pages,
        'current_page': paginated_tasks.page
    })

@main.route('/admin/tasks/all', methods=['GET'])
@token_required
@admin_required
def get_all_tasks_admin(current_user):
    """
    (Admin Only) Retrieve all tasks from all users.
    ---
    tags:
      - Admin
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: A list of all tasks from all users.
        schema:
          type: array
          items:
            $ref: '#/definitions/Task'
      403:
        description: Admin privilege required.
    """
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@main.route('/tasks/<int:id>', methods=['GET'])
@token_required
def get_task(current_user, id):
    """
    Retrieve a single specific task by its ID.
    ---
    tags:
      - Tasks
    security:
      - ApiKeyAuth: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the task to retrieve.
    responses:
      200:
        description: The requested task.
        schema:
          $ref: '#/definitions/Task'
      404:
        description: Task not found.
    """
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if not task:
        return jsonify({'message': 'Task not found!'}), 404
    return jsonify(task.to_dict())

@main.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    """
    Create a new task for the authenticated user.
    ---
    tags:
      - Tasks
    security:
      - ApiKeyAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
            description:
              type: string
            completed:
              type: boolean
    responses:
      201:
        description: Task created successfully.
        schema:
          $ref: '#/definitions/Task'
      400:
        description: Bad request (e.g., missing title).
    """
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'message': 'Title is a required field.'}), 400

    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        # FIX: Accept the 'completed' status from the request, defaulting to False
        completed=data.get('completed', False),
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@main.route('/tasks/<int:id>', methods=['PUT'])
@token_required
def update_task(current_user, id):
    """
    Update an existing task.
    ---
    tags:
      - Tasks
    security:
      - ApiKeyAuth: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the task to update.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            completed:
              type: boolean
    responses:
      200:
        description: Task updated successfully.
        schema:
          $ref: '#/definitions/Task'
      404:
        description: Task not found.
    """
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if not task:
        return jsonify({'message': 'Task not found!'}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    
    db.session.commit()
    return jsonify(task.to_dict())

@main.route('/tasks/<int:id>', methods=['DELETE'])
@token_required
def delete_task(current_user, id):
    """
    Delete a task.
    ---
    tags:
      - Tasks
    security:
      - ApiKeyAuth: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the task to delete.
    responses:
      200:
        description: Task deleted successfully.
      404:
        description: Task not found.
    """
    task = Task.query.filter_by(id=id, user_id=current_user.id).first()
    if not task:
        return jsonify({'message': 'Task not found!'}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'})

