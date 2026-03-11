"""
Authentication Tests
Tests for user registration, login, logout, token refresh, and JWT authentication
"""
import pytest
import json
from models import User, Role
from extensions import db


class TestUserRegistration:
    """Tests for user registration endpoint"""
    
    def test_register_new_user(self, client, db_session):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+1-555-0123'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@test.com'
        assert 'password' not in data['user']
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.check_password('password123')
    
    def test_register_duplicate_username(self, client, db_session):
        """Test registration with existing username"""
        # Create first user
        user = User(username='existinguser', email='existing@test.com', first_name='Existing', last_name='User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Try to register with same username
        response = client.post('/api/auth/register', json={
            'username': 'existinguser',
            'email': 'different@test.com',
            'password': 'password123',
            'first_name': 'Different',
            'last_name': 'User'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error'].lower()
    
    def test_register_duplicate_email(self, client, db_session):
        """Test registration with existing email"""
        # Create first user
        user = User(username='user1', email='duplicate@test.com', first_name='User', last_name='One')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Try to register with same email
        response = client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'duplicate@test.com',
            'password': 'password123',
            'first_name': 'User',
            'last_name': 'Two'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error'].lower()
    
    def test_register_missing_fields(self, client, db_session):
        """Test registration with missing required fields"""
        response = client.post('/api/auth/register', json={
            'username': 'incompleteuser',
            'password': 'password123'
            # Missing email, first_name, last_name
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error'].lower()
    
    def test_register_short_password(self, client, db_session):
        """Test registration with password too short"""
        response = client.post('/api/auth/register', json={
            'username': 'shortpass',
            'email': 'shortpass@test.com',
            'password': '12345',  # Only 5 characters
            'first_name': 'Short',
            'last_name': 'Pass'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'at least 6 characters' in data['error'].lower()


class TestUserLogin:
    """Tests for user login endpoint"""
    
    def test_login_success(self, client, db_session):
        """Test successful login"""
        # Create user
        user = User(username='loginuser', email='login@test.com', first_name='Login', last_name='User')
        user.set_password('password123')
        user.is_active = True
        db_session.add(user)
        db_session.commit()
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'loginuser'
    
    def test_login_invalid_username(self, client, db_session):
        """Test login with non-existent username"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid' in data['error'].lower()
    
    def test_login_invalid_password(self, client, db_session):
        """Test login with wrong password"""
        # Create user
        user = User(username='wrongpass', email='wrongpass@test.com', first_name='Wrong', last_name='Pass')
        user.set_password('correctpassword')
        db_session.add(user)
        db_session.commit()
        
        # Try wrong password
        response = client.post('/api/auth/login', json={
            'username': 'wrongpass',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid' in data['error'].lower()
    
    def test_login_inactive_account(self, client, db_session):
        """Test login with disabled account"""
        # Create inactive user
        user = User(username='inactive', email='inactive@test.com', first_name='Inactive', last_name='User')
        user.set_password('password123')
        user.is_active = False
        db_session.add(user)
        db_session.commit()
        
        # Try to login
        response = client.post('/api/auth/login', json={
            'username': 'inactive',
            'password': 'password123'
        })
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'disabled' in data['error'].lower()


class TestTokenOperations:
    """Tests for token refresh and verification"""
    
    def test_token_refresh(self, client, db_session):
        """Test refreshing access token"""
        # Create and login user
        user = User(username='refreshuser', email='refresh@test.com', first_name='Refresh', last_name='User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Login to get tokens
        login_response = client.post('/api/auth/login', json={
            'username': 'refreshuser',
            'password': 'password123'
        })
        tokens = json.loads(login_response.data)
        refresh_token = tokens['refresh_token']
        
        # Refresh the token
        response = client.post('/api/auth/refresh',
                              headers={'Authorization': f'Bearer {refresh_token}'})
        
        # Debug print
        if response.status_code != 200:
            print(f"Response: {response.status_code}, {response.get_json()}")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_verify_valid_token(self, client, db_session):
        """Test token verification with valid token"""
        # Create and login user
        user = User(username='verifyuser', email='verify@test.com', first_name='Verify', last_name='User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'username': 'verifyuser',
            'password': 'password123'
        })
        tokens = json.loads(login_response.data)
        access_token = tokens['access_token']
        
        # Verify token
        response = client.get('/api/auth/verify-token',
                            headers={'Authorization': f'Bearer {access_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
        assert data['user']['username'] == 'verifyuser'


class TestUserProfile:
    """Tests for user profile endpoints"""
    
    def test_get_profile(self, client, db_session):
        """Test getting user profile"""
        # Create and login user
        user = User(username='profileuser', email='profile@test.com', first_name='Profile', last_name='User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'username': 'profileuser',
            'password': 'password123'
        })
        tokens = json.loads(login_response.data)
        access_token = tokens['access_token']
        
        # Get profile
        response = client.get('/api/auth/me',
                            headers={'Authorization': f'Bearer {access_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == 'profileuser'
        assert data['user']['email'] == 'profile@test.com'
    
    def test_update_profile(self, client, db_session):
        """Test updating user profile"""
        # Create and login user
        user = User(username='updateuser', email='update@test.com', first_name='Update', last_name='User')
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'username': 'updateuser',
            'password': 'password123'
        })
        tokens = json.loads(login_response.data)
        access_token = tokens['access_token']
        
        # Update profile
        response = client.put('/api/auth/me',
                            headers={'Authorization': f'Bearer {access_token}'},
                            json={
                                'first_name': 'Updated',
                                'last_name': 'Name',
                                'phone': '+1-555-9999'
                            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['last_name'] == 'Name'
        assert data['user']['phone'] == '+1-555-9999'
    
    def test_change_password(self, client, db_session):
        """Test changing password"""
        # Create and login user
        user = User(username='changepass', email='changepass@test.com', first_name='Change', last_name='Pass')
        user.set_password('oldpassword')
        db_session.add(user)
        db_session.commit()
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'username': 'changepass',
            'password': 'oldpassword'
        })
        tokens = json.loads(login_response.data)
        access_token = tokens['access_token']
        
        # Change password
        response = client.post('/api/auth/change-password',
                             headers={'Authorization': f'Bearer {access_token}'},
                             json={
                                 'current_password': 'oldpassword',
                                 'new_password': 'newpassword123'
                             })
        
        assert response.status_code == 200
        
        # Verify old password doesn't work
        old_login = client.post('/api/auth/login', json={
            'username': 'changepass',
            'password': 'oldpassword'
        })
        assert old_login.status_code == 401
        
        # Verify new password works
        new_login = client.post('/api/auth/login', json={
            'username': 'changepass',
            'password': 'newpassword123'
        })
        assert new_login.status_code == 200
