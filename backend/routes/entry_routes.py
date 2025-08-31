from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Entry
from services.llm_service import llm_service
from services.database_service import DatabaseService

entry_bp = Blueprint('entries', __name__)

@entry_bp.route('', methods=['POST'])
@jwt_required()
def create_entry():
    try:
        user_id = int(get_jwt_identity())  # Convert to int
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        content = data.get('content', '').strip()
        entry_date_str = data.get('entry_date')  # YYYY-MM-DD format
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Parse entry_date or use today's date
        entry_date = None
        if entry_date_str:
            try:
                from datetime import datetime
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            from datetime import date
            entry_date = date.today()
        
        # Validate that entry_date is not in the future
        from datetime import date
        if entry_date > date.today():
            return jsonify({'error': 'Entry date cannot be in the future'}), 400
        
        # Try to generate embedding, but don't fail if it doesn't work
        embedding = None
        try:
            embedding = llm_service.generate_embedding(content)
            print(f"Generated embedding successfully: {len(embedding)} dimensions")
        except Exception as e:
            print(f"Warning: Could not generate embedding: {str(e)}")
            # Continue without embedding - the app should still work
        
        # Create entry with entry_date field
        entry = Entry(
            content=content,
            entry_date=entry_date,
            user_id=user_id,
            embedding=embedding  # Will be None if AI failed
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'entry': entry.to_dict(),
            'has_embedding': embedding is not None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating entry: {str(e)}")
        return jsonify({'error': str(e)}), 500

@entry_bp.route('', methods=['GET'])
@jwt_required()
def get_entries():
    try:
        user_id = int(get_jwt_identity())  # Convert to int
        
        # Get all entries for the user, sorted by entry_date (newest first), then by updated_at (newest first)
        entries = Entry.query.filter_by(user_id=user_id).order_by(
            Entry.entry_date.desc().nullslast(), 
            Entry.updated_at.desc()
        ).all()
        
        return jsonify({
            'entries': [entry.to_dict() for entry in entries]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@entry_bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    try:
        user_id = int(get_jwt_identity())  # Convert to int
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Check if entry belongs to user
        entry = Entry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Entry not found'}), 404
        
        # Update content and entry_date fields
        content = data.get('content', entry.content).strip() if data.get('content') is not None else entry.content
        entry_date_str = data.get('entry_date')  # YYYY-MM-DD format
        
        if not content:
            return jsonify({'error': 'Content cannot be empty'}), 400
        
        # Parse entry_date if provided
        entry_date = entry.entry_date  # Keep existing date if not provided
        if entry_date_str:
            try:
                from datetime import datetime
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            # Validate that entry_date is not in the future
            from datetime import date
            if entry_date > date.today():
                return jsonify({'error': 'Entry date cannot be in the future'}), 400
        
        # Try to generate new embedding for updated content
        embedding = entry.embedding  # Keep existing embedding if AI fails
        try:
            new_embedding = llm_service.generate_embedding(content)
            embedding = new_embedding
            print(f"Updated embedding successfully: {len(embedding)} dimensions")
        except Exception as e:
            print(f"Warning: Could not update embedding: {str(e)}")
            # Continue with existing embedding
        
        # Update entry
        entry.content = content
        entry.entry_date = entry_date
        entry.embedding = embedding
        
        db.session.commit()
        
        return jsonify({
            'entry': entry.to_dict(),
            'has_embedding': embedding is not None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating entry: {str(e)}")
        return jsonify({'error': str(e)}), 500

@entry_bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    try:
        user_id = int(get_jwt_identity())  # Convert to int
        
        # Check if entry belongs to user
        entry = Entry.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return jsonify({'error': 'Entry not found'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'message': 'Entry deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
