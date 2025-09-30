from datetime import datetime, timedelta
from extensions import db
import json
import secrets
from pgvector.sqlalchemy import Vector

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    entries = db.relationship('Entry', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def generate_reset_token(self) -> str:
        """Generate a secure password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        # Token expires in 1 hour
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token: str) -> bool:
        """Verify if the reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if datetime.utcnow() > self.reset_token_expires:
            # Token has expired, clear it
            self.reset_token = None
            self.reset_token_expires = None
            return False
        
        return self.reset_token == token
    
    def clear_reset_token(self):
        """Clear the reset token after password reset"""
        self.reset_token = None
        self.reset_token_expires = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Entry(db.Model):
    __tablename__ = 'entries'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)  # Date for the journal entry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When it was created in the system
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Store embedding as JSON text for backward compatibility
    embedding_json = db.Column(db.Text, nullable=True)
    # Native pgvector embedding for efficient similarity search
    embedding_vector = db.Column(Vector(768), nullable=True)  # 768 is typical for text embeddings
    
    @property
    def embedding(self):
        """Get embedding as list of floats - prefer vector column, fallback to JSON"""
        if self.embedding_vector is not None:
            return list(self.embedding_vector)
        elif self.embedding_json:
            try:
                return json.loads(self.embedding_json)
            except json.JSONDecodeError:
                return None
        return None
    
    @embedding.setter
    def embedding(self, value):
        """Set embedding from list of floats - store in both vector and JSON columns"""
        if value:
            self.embedding_vector = value  # pgvector column for efficient search
            self.embedding_json = json.dumps(value)  # JSON backup for compatibility
        else:
            self.embedding_vector = None
            self.embedding_json = None
    
    def to_dict(self):
        from datetime import timezone, timedelta
        
        # Define IST timezone (UTC+5:30)
        ist = timezone(timedelta(hours=5, minutes=30))
        
        # Convert UTC times to IST
        created_at_ist = self.created_at.replace(tzinfo=timezone.utc).astimezone(ist) if self.created_at else None
        updated_at_ist = self.updated_at.replace(tzinfo=timezone.utc).astimezone(ist) if self.updated_at else None
        
        return {
            'id': self.id,
            'content': self.content,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'created_at': created_at_ist.isoformat() if created_at_ist else None,
            'updated_at': updated_at_ist.isoformat() if updated_at_ist else None,
            'created_at_ist': created_at_ist.strftime('%Y-%m-%d %I:%M:%S %p IST') if created_at_ist else None,
            'updated_at_ist': updated_at_ist.strftime('%Y-%m-%d %I:%M:%S %p IST') if updated_at_ist else None,
            'user_id': self.user_id
        }
