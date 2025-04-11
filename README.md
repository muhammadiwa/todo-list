# To-Do List API Application

This is a simple To-Do List API application built with FastAPI and SQLite. It provides endpoints for user authentication, creating and managing checklists, and managing items within those checklists.

## Features

- User authentication with JWT
- Create, read, and delete checklists
- Create, read, update, and delete checklist items
- Toggle completion status of checklist items
- Rename checklist items

## API Endpoints

### Authentication

- `POST /api/login` - Login and get access token
- `POST /api/register` - Register a new user

### Checklists

- `GET /api/checklist` - Get all checklists for the current user
- `POST /api/checklist` - Create a new checklist
- `DELETE /api/checklist/{checklist_id}` - Delete a checklist by ID

### Checklist Items

- `GET /api/checklist/{checklist_id}/item` - Get all items in a checklist
- `POST /api/checklist/{checklist_id}/item` - Create a new item in a checklist
- `GET /api/checklist/{checklist_id}/item/{item_id}` - Get a specific item in a checklist
- `PUT /api/checklist/{checklist_id}/item/{item_id}` - Toggle the completion status of an item
- `DELETE /api/checklist/{checklist_id}/item/{item_id}` - Delete an item from a checklist
- `PUT /api/checklist/{checklist_id}/item/rename/{item_id}` - Rename an item in a checklist

## Setup and Installation

1. Clone the repository
2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure the JWT secret key
   Create a .env file in the root directory with your JWT secret key:
   ```
   JWT_SECRET_KEY=your_secure_secret_key
   ```
   You can generate a secure key with:
   ```
   openssl rand -hex 32
   ```
5. Run the application:
   ```
   python main.py
   ```
6. The API will be available at `http://localhost:8080/api`

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- Postman: `https://www.postman.com/payload-candidate-54469917/assesment/collection/7ot6t1r/todo-list-app?action=share&creator=42390035`
