from extensions import db
from models import Entry
from typing import List
from datetime import datetime, date
from pgvector.sqlalchemy import Vector
from sqlalchemy import text

class DatabaseService:
    """Service for database operations with efficient pgvector similarity search"""
    
    @staticmethod
    def find_similar_entries(embedding: List[float], user_id: int, limit: int = 10) -> List[Entry]:
        """
        Find entries similar to the given embedding using pgvector's efficient cosine similarity
        """
        try:
            print(f"🔍 Searching for similar entries for user {user_id} using pgvector")
            
            # Use pgvector's native cosine distance operator (<=>)
            # Note: cosine distance = 1 - cosine similarity, so smaller distance = more similar
            entries = db.session.query(Entry).filter(
                Entry.user_id == user_id,
                Entry.embedding_vector.isnot(None)
            ).order_by(
                Entry.embedding_vector.cosine_distance(embedding)
            ).limit(limit).all()
            
            print(f"📊 pgvector found {len(entries)} similar entries")
            
            # Optional: Log similarity scores for top entries (without extra queries)
            if entries:
                print(f"✅ Returning top {len(entries)} most similar entries efficiently")
            
            return entries
            
        except Exception as e:
            print(f"❌ Error in pgvector similarity search: {str(e)}")
            print("🔄 Falling back to JSON-based search...")
            
            # Fallback to old method if pgvector fails
            return DatabaseService._find_similar_entries_fallback(embedding, user_id, limit)
    
    @staticmethod
    def _find_similar_entries_fallback(embedding: List[float], user_id: int, limit: int = 10) -> List[Entry]:
        """
        Fallback method using JSON embeddings and Python cosine similarity
        """
        try:
            import math
            
            print(f"� Using fallback search for user {user_id}")
            
            # Get all entries for the user that have JSON embeddings
            all_entries = Entry.query.filter_by(user_id=user_id).filter(Entry.embedding_json.isnot(None)).all()
            print(f"📊 Found {len(all_entries)} entries with JSON embeddings in database")
            
            if not all_entries:
                print("❌ No entries with embeddings found")
                return []
            
            # Calculate similarities using pure Python
            similarities = []
            for entry in all_entries:
                if entry.embedding:
                    try:
                        # Pure Python cosine similarity
                        a, b = embedding, entry.embedding
                        dot_product = sum(x * y for x, y in zip(a, b))
                        magnitude_a = math.sqrt(sum(x * x for x in a))
                        magnitude_b = math.sqrt(sum(x * x for x in b))
                        
                        if magnitude_a == 0 or magnitude_b == 0:
                            similarity = 0
                        else:
                            similarity = dot_product / (magnitude_a * magnitude_b)
                            
                        similarities.append((entry, similarity))
                        print(f"📈 Entry ID {entry.id}: similarity = {similarity:.4f}")
                    except (ValueError, TypeError):
                        print(f"⚠️  Skipping entry ID {entry.id} due to invalid embedding")
                        continue
            
            # Sort by similarity (highest first) and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_entries = [entry for entry, _ in similarities[:limit]]
            print(f"✅ Returning {len(top_entries)} most similar entries")
            return top_entries
            
        except Exception as e:
            print(f"❌ Error in fallback similarity search: {str(e)}")
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
