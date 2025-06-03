# AdaptLearning Backend

A Django REST Framework-based backend for the AdaptLearning E-Learning and Examination System.

## Features

- User authentication and authorization (JWT)
- Course management
- Module and lesson organization
- Exam creation and management
- Progress tracking
- Swagger/OpenAPI documentation

## Tech Stack

- Python 3.x
- Django 5.1
- Django REST Framework
- SQLite (Development)
- JWT Authentication
- Swagger/OpenAPI Documentation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Wizard-Fingerz/AdaptLearningBE.git
cd AdaptLearningBE
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/docs.json`

## Project Structure

```
AdaptLearningBE/
├── elearning/          # Project settings
├── users/             # User management
├── courses/           # Course management
├── exams/            # Exam management
├── progress/         # Progress tracking
└── requirements.txt  # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 