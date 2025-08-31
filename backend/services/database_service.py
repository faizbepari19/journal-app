from extensions import db
from models import Entry
from typing import List
import numpy as np
from datetime import datetime, date

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
    @staticmethod
    def find_entries_by_date_query(query: str, user_id: int) -> List[Entry]:
        """
        Find entries by parsing date information from the query text
        """
        try:
            import re
            from datetime import datetime, date
            
            # Look for various date patterns in the query
            date_patterns = [
                r'(\d{1,2})\s*(?:st|nd|rd|th)?\s+(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+(\d{4})',
                r'(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+(\d{1,2})\s*(?:st|nd|rd|th)?\s*,?\s*(\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})/(\d{1,2})/(\d{4})',
                r'(\d{1,2})-(\d{1,2})-(\d{4})'
            ]
            
            found_dates = []
            query_lower = query.lower()
            
            # Month name to number mapping
            month_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 
                'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
                'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
            }
            
            # Try each pattern
            for pattern in date_patterns:
                matches = re.finditer(pattern, query_lower, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    try:
                        if len(groups) == 3:
                            if groups[1].isalpha():  # Day Month Year format
                                day = int(groups[0])
                                month = month_map.get(groups[1].lower())
                                year = int(groups[2])
                                if month:
                                    found_dates.append(date(year, month, day))
                            elif groups[0].isalpha():  # Month Day Year format
                                month = month_map.get(groups[0].lower())
                                day = int(groups[1])
                                year = int(groups[2])
                                if month:
                                    found_dates.append(date(year, month, day))
                            else:  # Numeric formats
                                # Try different interpretations
                                if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                                else:  # MM/DD/YYYY or DD/MM/YYYY
                                    # Assume MM/DD/YYYY for now
                                    month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                                found_dates.append(date(year, month, day))
                    except (ValueError, TypeError):
                        continue
            
            # Search for entries matching the found dates
            if found_dates:
                entries = []
                for search_date in found_dates:
                    date_entries = Entry.query.filter_by(user_id=user_id, entry_date=search_date).all()
                    entries.extend(date_entries)
                
                # If no entries found by entry_date, try created_at date
                if not entries:
                    for search_date in found_dates:
                        date_entries = Entry.query.filter_by(user_id=user_id).filter(
                            db.func.date(Entry.created_at) == search_date
                        ).all()
                        entries.extend(date_entries)
                
                return entries
            
            return []
            
        except Exception as e:
            print(f"Error in date-based search: {str(e)}")
            return []
    
    @staticmethod
    def find_entries_by_date_query(query: str, user_id: int) -> List[Entry]:
        """
        Find entries by parsing date information from the query text
        """
        try:
            import re
            from datetime import datetime, date
            
            # Look for various date patterns in the query
            date_patterns = [
                r'(\d{1,2})\s*(?:st|nd|rd|th)?\s+(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+(\d{4})',
                r'(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+(\d{1,2})\s*(?:st|nd|rd|th)?\s*,?\s*(\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})/(\d{1,2})/(\d{4})',
                r'(\d{1,2})-(\d{1,2})-(\d{4})'
            ]
            
            found_dates = []
            query_lower = query.lower()
            
            # Month name to number mapping
            month_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 
                'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
                'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
            }
            
            # Try each pattern
            for pattern in date_patterns:
                matches = re.finditer(pattern, query_lower, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    try:
                        if len(groups) == 3:
                            if groups[1].isalpha():  # Day Month Year format
                                day = int(groups[0])
                                month = month_map.get(groups[1].lower())
                                year = int(groups[2])
                                if month:
                                    found_dates.append(date(year, month, day))
                            elif groups[0].isalpha():  # Month Day Year format
                                month = month_map.get(groups[0].lower())
                                day = int(groups[1])
                                year = int(groups[2])
                                if month:
                                    found_dates.append(date(year, month, day))
                            else:  # Numeric formats
                                # Try different interpretations
                                if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                                else:  # MM/DD/YYYY or DD/MM/YYYY
                                    # Assume MM/DD/YYYY for now
                                    month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                                found_dates.append(date(year, month, day))
                    except (ValueError, TypeError):
                        continue
            
            # Search for entries matching the found dates
            if found_dates:
                entries = []
                for search_date in found_dates:
                    date_entries = Entry.query.filter_by(user_id=user_id, entry_date=search_date).all()
                    entries.extend(date_entries)
                
                # If no entries found by entry_date, try created_at date
                if not entries:
                    for search_date in found_dates:
                        date_entries = Entry.query.filter_by(user_id=user_id).filter(
                            db.func.date(Entry.created_at) == search_date
                        ).all()
                        entries.extend(date_entries)
                
                return entries
            
            return []
            
        except Exception as e:
            print(f"Error in date-based search: {str(e)}")
            return []
    
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
