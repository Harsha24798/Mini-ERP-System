"""
Authentication Routes
Handles user registration, login, logout, token refresh, and password management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from extensions import db
from models import User, Role
from utils.auth import generate_user_claims, get_current_user, token_required
from datetime import timedelta


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
        {
            "username": "string (required)",
            "email": "string (required)",
            "password": "string (required, min 6 chars)",
            "first_name": "string (required)",
            "last_name": "string (required)",
            "phone": "string (optional)"
        }
    
    Returns:
        201: User created successfully with user data
        400: Validation error or user already exists
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate password length
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        
        # Assign default "Staff" role to new users
        default_role = Role.query.filter_by(name='Staff').first()
        if default_role:
            user.roles.append(default_role)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens
    
    Request body:
        {
            "username": "string (required)",
            "password": "string (required)"
        }
    
    Returns:
        200: Login successful with access and refresh tokens
        401: Invalid credentials
        403: Account disabled
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check if account is active
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Update last login
        user.update_last_login()
        db.session.commit()
        
        # Generate custom claims
        additional_claims = generate_user_claims(user)
        
        # Create tokens (convert user.id to string for JWT)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))  # Convert string back to int
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Generate fresh access token with updated claims
        additional_claims = generate_user_claims(user)
        access_token = create_access_token(
            identity=str(user.id),  # Convert to string for JWT
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout user (client should discard tokens)
    
    Note: Since we're using stateless JWT, actual token invalidation 
    would require a token blacklist (can be implemented later with Redis)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        200: Logout successful
    """
    # In a production app, you would add the token to a blacklist here
    # For now, we rely on client-side token removal
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_profile():
    """
    Get current user profile
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        200: User profile data
        401: Invalid token
        404: User not found
    """
    try:
        user = get_current_user()
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    """
    Update current user profile
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request body:
        {
            "first_name": "string (optional)",
            "last_name": "string (optional)",
            "email": "string (optional)",
            "phone": "string (optional)"
        }
    
    Returns:
        200: Profile updated successfully
        400: Validation error
        401: Invalid token
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Profile update failed', 'details': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    Change current user password
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request body:
        {
            "current_password": "string (required)",
            "new_password": "string (required, min 6 chars)"
        }
    
    Returns:
        200: Password changed successfully
        400: Validation error
        401: Invalid current password
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Validate new password length
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Password change failed', 'details': str(e)}), 500


@auth_bp.route('/verify-token', methods=['GET'])
@token_required
def verify_token():
    """
    Verify if the provided token is valid
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        200: Token is valid with user info
        401: Token is invalid or expired
    """
    try:
        user = get_current_user()
        jwt_data = get_jwt()
        
        return jsonify({
            'valid': True,
            'user': user.to_dict(),
            'token_data': {
                'roles': jwt_data.get('roles', []),
                'permissions': jwt_data.get('permissions', [])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token verification failed', 'details': str(e)}), 500
