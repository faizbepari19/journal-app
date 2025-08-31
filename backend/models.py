from datetime import datetime
from extensions import db
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    entries = db.relationship('Entry', backref='author', lazy=True, cascade='all, delete-orphan')
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Store embedding as JSON text for now (can be upgraded to pgvector later)
    embedding_json = db.Column(db.Text, nullable=True)
    
    @property
    def embedding(self):
        """Get embedding as list of floats"""
        if self.embedding_json:
            try:
                return json.loads(self.embedding_json)
            except json.JSONDecodeError:
                return None
        return None
    
    @embedding.setter
    def embedding(self, value):
        """Set embedding from list of floats"""
        if value:
            self.embedding_json = json.dumps(value)
        else:
            self.embedding_json = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }
