# Task Manager API

A comprehensive, feature-rich RESTful API for a task manager application built with Flask. This project includes user authentication (JWT), role-based access control, CRUD operations for tasks, pagination, filtering, and automated API documentation.

## Features

- **Full CRUD Operations:** Create, Read, Update, and Delete tasks.
- **User Authentication:** Secure JWT-based authentication for user registration and login.
- **Role-Based Access Control:** Differentiates between regular users and administrators.
  - Users can only manage their own tasks.
  - Admins have access to an exclusive endpoint to view all tasks from all users.
- **Pagination:** The `/tasks` endpoint is paginated to handle large datasets efficiently.
- **Filtering:** Filter tasks by their completion status (e.g., `?completed=true`).
- **Automated API Documentation:** Interactive API documentation powered by Swagger (Flasgger).
- **Unit Tested:** Comes with a comprehensive test suite with high code coverage.

---

## Project Structure

The project follows a standard and scalable Flask application structure, separating concerns into different modules.

TaskManagerAPI/ ├── app/ │ ├── init.py │ ├── auth.py │ ├── decorators.py │ ├── extensions.py │ ├── models.py │ └── routes.py ├── tests/ │ └── test_app.py ├── .env ├── config.py ├── README.md └── run.py

### File Descriptions

| File                | Purpose                                                              |
| ------------------- | -------------------------------------------------------------------- |
| `run.py`            | The main script to start the application server.                     |
| `config.py`         | Stores configuration classes for the application.                    |
| `.env`              | Holds environment variables like the `SECRET_KEY`.                   |
| `requirements.txt`  | Lists all the Python packages the project depends on.                |
| `app/__init__.py`   | **Application Factory**: Creates and configures the Flask app.       |
| `app/routes.py`     | Defines the main API endpoints for managing tasks (CRUD).            |
| `app/auth.py`       | Defines the routes for user registration and login.                  |
| `app/models.py`     | Defines the database structure (`User` and `Task` tables).           |
| `app/decorators.py` | Contains custom security checks for routes (e.g., `token_required`). |
| `app/extensions.py` | Initializes shared extensions like the database.                     |
| `tests/test_app.py` | Contains all the unit tests for the API.                             |

---

## API Documentation

The API documentation is automatically generated and served using Swagger UI. Once the application is running, you can access the interactive documentation by navigating to the following URL in your browser:

[**http://127.0.0.1:5000/apidocs/**](http://127.0.0.1:5000/apidocs/)

---

## Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

- Python 3.10+
- `pip` and `venv`

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

````bash
# Navigate to the project's root directory
cd path/to/your/TaskManagerAPI

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

### 3. Install Dependencies
Install all the required packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt


````

### 4. Environment Configuration

This application requires a `.env` file in the project's root directory to store sensitive configuration variables.

**a. Create the `.env` file:**
Create a file named `.env` at the root of the project.

**b. Define Environment Variables:**
Add the following variables to your `.env` file:

```env
# A strong, random secret key for signing tokens.
SECRET_KEY='your_super_secret_random_key_here'

# The path to your SQLite database file.
DATABASE_URL='sqlite:///tasks.db'
```

**c. Generate a Secret Key:**
To generate a secure, random SECRET_KEY, run the following command in your terminal and paste the output into the .env file:

```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

---

## Running the Application

Once the setup is complete, you can start the Flask development server with this command:

```bash
flask run
```

Or alternatively:

```bash
python run.py
```

The API will now be running at http://127.0.0.1:5000.

---

## Running the Tests

The project includes a full suite of unit tests to ensure the API is working correctly.

**1. Execute All Tests**
To run the tests, execute the following command from the project's root directory:

```bash
pytest
```

**2. Get a Test Coverage Report**
To see how much of your application code is covered by the tests, run this command:

```bash
pytest --cov=app
```

For a more detailed, interactive HTML report, run:

```bash
pytest --cov=app --cov-report=html
```

This will generate an htmlcov directory. Open the index.html file inside it to view the full report.
