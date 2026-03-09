"""
Unit tests for database models
"""
import pytest
from models import User, Role, Permission
from app import db


class TestUserModel:
    """Tests for User model"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('password123')
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.full_name == 'Test User'
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')
    
    def test_user_password_hashing(self, db_session):
        """Test password hashing"""
        user = User(
            username='testuser2',
            email='test2@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('mypassword')
        
        assert user.password_hash != 'mypassword'
        assert user.check_password('mypassword')
    
    def test_user_role_relationship(self, db_session):
        """Test user-role many-to-many relationship"""
        user = User(
            username='testuser3',
            email='test3@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('password')
        
        role = Role(name='TestRole', description='Test role')
        user.roles.append(role)
        
        db_session.add(user)
        db_session.commit()
        
        assert user.has_role('TestRole')
        assert not user.has_role('NonExistentRole')
    
    def test_user_permission_check(self, db_session):
        """Test user permission checking through roles"""
        user = User(
            username='testuser4',
            email='test4@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('password')
        
        role = Role(name='Editor', description='Can edit')
        permission = Permission(
            name='edit.content',
            resource='content',
            action='update',
            description='Edit content'
        )
        role.permissions.append(permission)
        user.roles.append(role)
        
        db_session.add(user)
        db_session.commit()
        
        assert user.has_permission('edit.content')
        assert not user.has_permission('delete.content')
    
    def test_user_to_dict(self, db_session):
        """Test user serialization"""
        user = User(
            username='testuser5',
            email='test5@example.com',
            first_name='Test',
            last_name='User',
            phone='+1-555-0001'
        )
        user.set_password('password')
        
        db_session.add(user)
        db_session.commit()
        
        user_dict = user.to_dict()
        
        assert user_dict['username'] == 'testuser5'
        assert user_dict['email'] == 'test5@example.com'
        assert user_dict['full_name'] == 'Test User'
        assert 'password_hash' not in user_dict
        assert 'created_at' in user_dict
