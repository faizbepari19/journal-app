from extensions import db
from models import Entry
from typing import List
import numpy as np

class DatabaseService:
    """Service for database operations with simplified vector similarity search"""
    
    @staticmethod
    def cosine_similarity(a, b):
        """Calculate cosine similarity between two vectors"""
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    @staticmethod
    def find_similar_entries(embedding: List[float], user_id: int, limit: int = 10) -> List[Entry]:
        """
        Find entries similar to the given embedding using cosine similarity
        """
        try:
            # Get all entries for the user that have embeddings
            all_entries = Entry.query.filter_by(user_id=user_id).filter(Entry.embedding_json.isnot(None)).all()
            
            if not all_entries:
                return []
            
            # Calculate similarities
            similarities = []
            for entry in all_entries:
                if entry.embedding:
                    try:
                        similarity = DatabaseService.cosine_similarity(embedding, entry.embedding)
                        similarities.append((entry, similarity))
                    except (ValueError, TypeError):
                        # Skip entries with invalid embeddings
                        continue
            
            # Sort by similarity (highest first) and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [entry for entry, _ in similarities[:limit]]
            
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            # Fallback to recent entries
            return Entry.query.filter_by(user_id=user_id).order_by(Entry.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def create_entry_with_embedding(content: str, user_id: int, embedding: List[float]) -> Entry:
        """Create a new entry with its embedding"""
        entry = Entry(
            content=content,
            user_id=user_id
        )
        entry.embedding = embedding
        db.session.add(entry)
        db.session.commit()
        return entry
    
    @staticmethod
    def update_entry_with_embedding(entry_id: int, content: str, embedding: List[float]) -> Entry:
        """Update an existing entry with new content and embedding"""
        entry = Entry.query.get_or_404(entry_id)
        entry.content = content
        entry.embedding = embedding
        db.session.commit()
        return entry
