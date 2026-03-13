# CLIP Vector Search - Setup Guide

## Project Structure

```
Vector-Search/
├── backend/           # FastAPI backend
│   ├── app/
│   ├── scripts/
│   └── requirements.txt
└── frontend/          # Streamlit frontend
    ├── pages/
    ├── src/
    ├── app.py
    └── requirements.txt
```

## Running the Application

### 1. Start the FastAPI Backend

Open a terminal in the `backend` directory and run:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### 2. Create Test Data (First Time Only)

In another terminal, create test users and images:

```bash
cd backend
python scripts/create_test_data.py
```

This creates:
- **Admin User**: username: `admin`, password: `admin123`
- **Test User 1**: username: `user1`, password: `user123`
- **Test User 2**: username: `user2`, password: `user123`

### 3. Start the Streamlit Frontend

In another terminal:

```bash
cd frontend
streamlit run app.py
```

The frontend will be available at: http://localhost:8501

### 4. Login

Use the test credentials to login:
- **Username**: `admin`
- **Password**: `admin123`

## Architecture

- **Backend (FastAPI)**: Handles authentication, user management, and provides REST API
- **Frontend (Streamlit)**: User interface that calls the backend API
- **Database**: SQLite database for users and images
- **Authentication**: JWT-based authentication with bearer tokens

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout

### Users
- `GET /api/users/` - List all users (admin only)
- `GET /api/users/{user_id}` - Get user by ID
- `POST /api/users/` - Create new user (admin only)

### Images
- `GET /api/images/` - List all images
- `GET /api/images/{image_id}` - Get image by ID
- `POST /api/images/` - Create new image
- `GET /api/images/user/{user_id}` - Get images by user

### Search
- `POST /api/search/text` - Search images by text
- `POST /api/search/image` - Search images by image
