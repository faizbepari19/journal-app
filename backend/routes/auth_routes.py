import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Optional: Send welcome email (non-blocking)
        try:
            from services.email_service import email_service
            email_service.send_welcome_email(user.email, user.username)
        except Exception as email_error:
            print(f"⚠️ Welcome email failed to send: {str(email_error)}")
            # Don't fail registration if welcome email fails
        
        return jsonify({'message': 'User registered successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        email = data['email']
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token with string identity
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = int(get_jwt_identity())  # Convert back to int
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Return success message even if user doesn't exist (security best practice)
            return jsonify({'message': 'If that email is registered, a password reset link has been sent.'}), 200
        
        # Check if email service is configured
        try:
            from services.email_service import email_service
        except ValueError as e:
            return jsonify({'error': 'Email service not configured. Please contact support.'}), 503
        
        try:
            # Generate reset token
            reset_token = user.generate_reset_token()
            
            # Save token to database
            db.session.commit()
            
            # Send password reset email
            email_sent = email_service.send_password_reset_email(
                to_email=user.email,
                reset_token=reset_token,
                username=user.username
            )
            
            if email_sent:
                print(f"✅ Password reset email sent successfully to {user.email}")
            else:
                print(f"❌ Failed to send password reset email to {user.email}")
            
            return jsonify({'message': 'If that email is registered, a password reset link has been sent.'}), 200
            
        except Exception as email_error:
            print(f"❌ Error in password reset process: {str(email_error)}")
            # Rollback the token generation if email fails
            db.session.rollback()
            # Still return success message for security
            return jsonify({'message': 'If that email is registered, a password reset link has been sent.'}), 200
        
    except Exception as e:
        print(f"❌ Error in forgot_password endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred processing your request'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using the token from email"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('new_password'):
            return jsonify({'error': 'Token and new password are required'}), 400
        
        token = data['token']
        new_password = data['new_password']
        
        # Validate password strength
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Find user by token
        user = User.query.filter_by(reset_token=token).first()
        
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Verify token is still valid
        if not user.verify_reset_token(token):
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Update password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.clear_reset_token()  # Clear the reset token
        
        db.session.commit()
        
        print(f"✅ Password reset successful for user: {user.email}")
        
        return jsonify({'message': 'Password reset successful. You can now log in with your new password.'}), 200
        
    except Exception as e:
        print(f"❌ Error in reset_password endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred processing your request'}), 500


@auth_bp.route('/validate-reset-token', methods=['POST'])
def validate_reset_token():
    """Validate if a reset token is still valid (for frontend validation)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token'):
            return jsonify({'error': 'Token is required'}), 400
        
        token = data['token']
        
        # Find user by token
        user = User.query.filter_by(reset_token=token).first()
        
        if not user or not user.verify_reset_token(token):
            return jsonify({'valid': False, 'message': 'Invalid or expired reset token'}), 200
        
        return jsonify({
            'valid': True, 
            'message': 'Token is valid',
            'email': user.email  # Can be used to show which email the reset is for
        }), 200
        
    except Exception as e:
        print(f"❌ Error in validate_reset_token endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500