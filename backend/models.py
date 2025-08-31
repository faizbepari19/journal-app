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
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)  # Date for the journal entry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When it was created in the system
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
