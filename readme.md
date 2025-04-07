# UPCampus Backend

A Django-based backend API for the UPCampus project.

## Setup Guide

### Prerequisites
- Python 3.10 or higher
- Git
- pip (Python package installer)

## Clone the Repository

```bash
git clone git@github.com:CMSC-128-A2/UPCampus-backend.git
cd UPCampus-backend
```

## Setup Instructions

### For macOS

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your database and other configurations
   ```

4. **Apply migrations**
   ```bash
   python src/manage.py migrate
   ```

5. **Run the development server**
   ```bash
   python src/manage.py runserver
   ```

### For Windows

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env file with your database and other configurations
   ```

4. **Apply migrations**
   ```bash
   python src\manage.py migrate
   ```

5. **Run the development server**
   ```bash
   python src\manage.py runserver
   ```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Build and start the Docker container
docker build -t upcampus-backend .
docker run -p 8000:8000 upcampus-backend
```

## API Documentation

The API documentation is available at `/api/docs/` when the server is running.

## Development

Remember to activate your virtual environment each time you work on the project:

- macOS: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`
