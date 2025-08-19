# API Authentication Integration Guide

## Overview
The API now supports Token-based authentication for secure access to endpoints. Users can register, login, and access protected resources using tokens.

## Authentication Endpoints

### 1. User Registration
```
POST /api/auth/register/
```

**Request Body:**
```json
{
    "username": "your_username",
    "email": "your_email@example.com", 
    "password": "your_password",
    "password_confirm": "your_password",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "your_username",
        "email": "your_email@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### 2. User Login
```
POST /api/auth/login/
```

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "your_username",
        "email": "your_email@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### 3. User Logout
```
POST /api/auth/logout/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

### 4. User Profile
```
GET /api/auth/profile/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-08-19T10:30:00Z",
    "last_login": "2025-08-19T11:00:00Z"
}
```

### 5. Update Profile
```
PUT /api/auth/profile/update/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Request Body:**
```json
{
    "email": "new_email@example.com",
    "first_name": "Jane",
    "last_name": "Smith"
}
```

## Using Authentication in Requests

### Headers Required for Protected Endpoints
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### Current Endpoint Protection Status

**Public Endpoints (No Auth Required):**
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/predictions/current-week/`
- `GET /api/predictions/dashboard-cards/`
- `GET /api/predictions/chart-data/`
- `GET /api/market-data/history/`

**Protected Endpoints (Auth Required):**
- `POST /api/auth/logout/`
- `GET /api/auth/profile/`
- `PUT /api/auth/profile/update/`
- `POST /api/predictions/simulate-weeks/` (recommended for protection)

## Testing with Postman

### 1. Setup Authentication
1. Register or login to get your token
2. Go to Authorization tab in Postman
3. Select "API Key" type
4. Set Key: `Authorization`
5. Set Value: `Token your_token_here`
6. Set Add to: `Header`

### 2. Alternative Method
Add header manually:
- Key: `Authorization`
- Value: `Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

## Streamlit Integration

### 1. Login Flow
```python
import streamlit as st
import requests

def authenticate_user(username, password):
    """Login user and get token"""
    url = "http://localhost:8000/api/auth/login/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['token'], result['user']
    else:
        st.error("Login failed")
        return None, None

def register_user(username, email, password, first_name="", last_name=""):
    """Register new user"""
    url = "http://localhost:8000/api/auth/register/"
    data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
        "first_name": first_name,
        "last_name": last_name
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 201:
        result = response.json()
        return result['token'], result['user']
    else:
        st.error(f"Registration failed: {response.json()}")
        return None, None

# Example Streamlit auth sidebar
def show_auth_sidebar():
    with st.sidebar:
        st.header("Authentication")
        
        if 'token' not in st.session_state:
            auth_mode = st.radio("Choose:", ["Login", "Register"])
            
            if auth_mode == "Login":
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login")
                    
                    if submit:
                        token, user = authenticate_user(username, password)
                        if token:
                            st.session_state.token = token
                            st.session_state.user = user
                            st.rerun()
            
            else:  # Register
                with st.form("register_form"):
                    username = st.text_input("Username")
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    first_name = st.text_input("First Name")
                    last_name = st.text_input("Last Name")
                    submit = st.form_submit_button("Register")
                    
                    if submit:
                        token, user = register_user(username, email, password, first_name, last_name)
                        if token:
                            st.session_state.token = token
                            st.session_state.user = user
                            st.rerun()
        else:
            st.success(f"Welcome, {st.session_state.user['username']}!")
            if st.button("Logout"):
                logout_user(st.session_state.token)
                del st.session_state.token
                del st.session_state.user
                st.rerun()

def logout_user(token):
    """Logout user"""
    url = "http://localhost:8000/api/auth/logout/"
    headers = {"Authorization": f"Token {token}"}
    requests.post(url, headers=headers)
```

### 2. Making Authenticated API Calls
```python
def make_authenticated_request(endpoint, token, method="GET", data=None):
    """Make authenticated API request"""
    url = f"http://localhost:8000{endpoint}"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    
    return response

# Example usage
if 'token' in st.session_state:
    # Get dashboard data with authentication
    response = make_authenticated_request(
        "/api/predictions/dashboard-cards/", 
        st.session_state.token
    )
    
    if response.status_code == 200:
        dashboard_data = response.json()
        # Use dashboard_data...
```

## Swagger UI Authentication

1. Go to http://localhost:8000/ (Swagger UI)
2. Click "Authorize" button (lock icon)
3. Enter: `Token your_token_here`
4. Click "Authorize"
5. Now you can test protected endpoints

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `201`: Created (registration successful)
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)

### Example Error Responses
```json
{
    "username": ["Username already exists"],
    "email": ["Email already exists"]
}
```

```json
{
    "detail": "Invalid token."
}
```

## Next Steps

1. **Test Authentication**: Use Postman or Swagger to test registration/login
2. **Implement in Streamlit**: Add the auth sidebar to your dashboard
3. **Protect More Endpoints**: Gradually add authentication to sensitive endpoints
4. **User Management**: Consider adding user roles/permissions if needed

## Security Notes

- Tokens don't expire by default (consider adding expiration in production)
- Store tokens securely in Streamlit session state
- Never expose tokens in URLs or logs
- Use HTTPS in production
- Consider implementing refresh tokens for better security
