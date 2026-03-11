"""
Authentication Utilities
Handles JWT token generation, validation, and user identity management
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from models import User, Permission


def generate_user_claims(user):
    """
    Generate custom claims for JWT token
    
    Args:
        user: User model instance
        
    Returns:
        dict: Custom claims with user roles and permissions
    """
    roles = [role.name for role in user.roles]
    permissions = []
    
    for role in user.roles:
        for permission in role.permissions:
            perm_name = permission.name
            if perm_name not in permissions:
                permissions.append(perm_name)
    
    return {
        'roles': roles,
        'permissions': permissions,
        'email': user.email,
        'full_name': user.full_name
    }


def get_current_user():
    """
    Get the current authenticated user from JWT token
    
    Returns:
        User: Current user instance or None
    """
    try:
        user_identity = get_jwt_identity()
        if user_identity:
            # Convert string ID back to integer
            user_id = int(user_identity)
            return User.query.get(user_id)
    except Exception:
        pass
    return None


def token_required(fn):
    """
    Decorator to require valid JWT token for endpoint access
    
    Usage:
        @token_required
        def protected_route():
            user = get_current_user()
            return jsonify(user.to_dict())
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.is_active:
                return jsonify({'error': 'Account is disabled'}), 403
            
            return fn(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401
    
    return wrapper


def role_required(*role_names):
    """
    Decorator to require specific roles for endpoint access
    
    Args:
        *role_names: Variable number of role names (Admin, Manager, Staff, etc.)
        
    Usage:
        @role_required('Admin', 'Manager')
        def admin_only_route():
            return jsonify({'message': 'Admin access granted'})
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user = get_current_user()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if not user.is_active:
                    return jsonify({'error': 'Account is disabled'}), 403
                
                # Check if user has any of the required roles
                user_roles = [role.name for role in user.roles]
                if not any(role in user_roles for role in role_names):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_roles': list(role_names),
                        'user_roles': user_roles
                    }), 403
                
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
        
        return wrapper
    return decorator


def permission_required(*permission_names):
    """
    Decorator to require specific permissions for endpoint access
    
    Args:
        *permission_names: Variable number of permission names (e.g., 'user.create', 'product.update')
        
    Usage:
        @permission_required('product.create', 'product.update')
        def create_product():
            return jsonify({'message': 'Product created'})
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user = get_current_user()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if not user.is_active:
                    return jsonify({'error': 'Account is disabled'}), 403
                
                # Check if user has all required permissions
                missing_permissions = []
                for perm_name in permission_names:
                    if not user.has_permission(perm_name):
                        missing_permissions.append(perm_name)
                
                if missing_permissions:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'missing_permissions': missing_permissions
                    }), 403
                
                return fn(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
        
        return wrapper
    return decorator


def admin_required(fn):
    """
    Decorator to require Admin role
    Shorthand for @role_required('Admin')
    """
    return role_required('Admin')(fn)
