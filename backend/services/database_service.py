from extensions import db
from models import Entry
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, date
from pgvector.sqlalchemy import Vector
from sqlalchemy import text

class DatabaseService:
    """Refactored database service with unified search functionality"""
    
    @staticmethod
    def search_entries(
        user_id: int,
        query: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        date_filter: Optional[Dict[str, Any]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Entry]:
        """
        Unified search method that handles all search scenarios:
        - Vector similarity search (with embedding)
        - Date-based search (with query parsing or explicit dates) 
        - Combined vector + date filtering
        - Pure date range search
        
        Args:
            user_id: User ID to filter entries
            query: Natural language query (for date parsing if no embedding)
            embedding: Vector embedding for semantic search
            date_filter: LLM-extracted date filter dict
            start_date: Explicit start date for filtering
            end_date: Explicit end date for filtering  
            limit: Maximum number of entries to return
            
        Returns:
            List of matching entries, ordered by relevance
        """
        try:
            print(f"🔍 Unified search - User: {user_id}, Query: '{query}', Has embedding: {embedding is not None}")
            
            # Step 1: Determine date constraints from various sources
            search_start_date, search_end_date = DatabaseService._resolve_date_constraints(
                query, date_filter, start_date, end_date
            )
            
            # Step 2: Perform the appropriate search strategy
            if embedding:
                # Vector similarity search (with optional date filtering)
                entries = DatabaseService._vector_search(
                    embedding, user_id, search_start_date, search_end_date, limit
                )
                print(f"🧠 Vector search found {len(entries)} entries")
            else:
                # Pure date-based search
                entries = DatabaseService._date_only_search(
                    query, user_id, search_start_date, search_end_date, limit
                )
                print(f"📅 Date-only search found {len(entries)} entries")
            
            return entries
            
        except Exception as e:
            print(f"❌ Error in unified search: {str(e)}")
            return []
    
    @staticmethod
    def _resolve_date_constraints(
        query: Optional[str],
        date_filter: Optional[Dict[str, Any]],
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> Tuple[Optional[date], Optional[date]]:
        """
        Resolve date constraints from multiple sources with priority:
        1. Explicit start_date/end_date parameters (highest priority)
        2. LLM date_filter 
        3. Regex parsing from query (lowest priority)
        """
        # Priority 1: Explicit dates
        if start_date and end_date:
            print(f"📅 Using explicit dates: {start_date} to {end_date}")
            return start_date, end_date
        
        # Priority 2: LLM date filter
        if date_filter and date_filter.get('has_date_filter'):
            try:
                start_str = date_filter.get('start_date')
                end_str = date_filter.get('end_date')
                if start_str and end_str:
                    start_parsed = datetime.strptime(start_str, '%Y-%m-%d').date()
                    end_parsed = datetime.strptime(end_str, '%Y-%m-%d').date()
                    print(f"📅 Using LLM dates: {start_parsed} to {end_parsed}")
                    return start_parsed, end_parsed
            except (ValueError, TypeError) as e:
                print(f"⚠️ Failed to parse LLM dates: {e}")
        
        # Priority 3: Regex parsing from query
        if query:
            parsed_dates = DatabaseService._parse_dates_from_query(query)
            if parsed_dates:
                print(f"📅 Using parsed dates: {parsed_dates[0]} to {parsed_dates[1]}")
                return parsed_dates
        
        print("📅 No date constraints found")
        return None, None
    
    @staticmethod
    def _vector_search(
        embedding: List[float],
        user_id: int, 
        start_date: Optional[date],
        end_date: Optional[date],
        limit: int
    ) -> List[Entry]:
        """Perform vector similarity search with optional date filtering"""
        try:
            print(f"🧠 Vector search with date filter: {start_date} to {end_date}")
            
            # Base query for vector similarity
            query = db.session.query(Entry).filter(
                Entry.user_id == user_id,
                Entry.embedding_vector.isnot(None)
            )
            
            # Add date filtering if specified
            if start_date and end_date:
                query = query.filter(
                    db.or_(
                        db.and_(
                            Entry.entry_date >= start_date,
                            Entry.entry_date <= end_date
                        ),
                        db.and_(
                            Entry.entry_date.is_(None),
                            db.func.date(Entry.created_at) >= start_date,
                            db.func.date(Entry.created_at) <= end_date
                        )
                    )
                )
            
            # Apply vector similarity ordering
            entries = query.order_by(
                Entry.embedding_vector.cosine_distance(embedding)
            ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            print(f"❌ pgvector search failed: {e}, falling back...")
            return DatabaseService._fallback_vector_search(
                embedding, user_id, start_date, end_date, limit
            )
    
    @staticmethod
    def _fallback_vector_search(
        embedding: List[float],
        user_id: int,
        start_date: Optional[date], 
        end_date: Optional[date],
        limit: int
    ) -> List[Entry]:
        """Fallback vector search using JSON embeddings and Python similarity"""
        try:
            import math
            print("🔄 Using fallback vector search")
            
            # Get base entries
            query = Entry.query.filter_by(user_id=user_id).filter(Entry.embedding_json.isnot(None))
            
            # Apply date filtering
            if start_date and end_date:
                query = query.filter(
                    db.or_(
                        db.and_(
                            Entry.entry_date >= start_date,
                            Entry.entry_date <= end_date
                        ),
                        db.and_(
                            Entry.entry_date.is_(None),
                            db.func.date(Entry.created_at) >= start_date,
                            db.func.date(Entry.created_at) <= end_date
                        )
                    )
                )
            
            all_entries = query.all()
            
            # Calculate similarities
            similarities = []
            for entry in all_entries:
                if entry.embedding:
                    try:
                        # Cosine similarity calculation
                        a, b = embedding, entry.embedding
                        dot_product = sum(x * y for x, y in zip(a, b))
                        magnitude_a = math.sqrt(sum(x * x for x in a))
                        magnitude_b = math.sqrt(sum(x * x for x in b))
                        
                        similarity = dot_product / (magnitude_a * magnitude_b) if magnitude_a and magnitude_b else 0
                        similarities.append((entry, similarity))
                    except (ValueError, TypeError):
                        continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [entry for entry, _ in similarities[:limit]]
            
        except Exception as e:
            print(f"❌ Fallback search failed: {e}")
            return []
    
    @staticmethod
    def _date_only_search(
        query: Optional[str],
        user_id: int,
        start_date: Optional[date],
        end_date: Optional[date], 
        limit: int
    ) -> List[Entry]:
        """Perform pure date-based search without vector similarity"""
        try:
            # If no date constraints, try to parse from query
            if not start_date or not end_date:
                if query:
                    parsed = DatabaseService._parse_dates_from_query(query)
                    if parsed:
                        start_date, end_date = parsed
                
                if not start_date or not end_date:
                    print("❌ No valid dates for date-only search")
                    return []
            
            print(f"📅 Date-only search: {start_date} to {end_date}")
            
            # Search by entry_date first
            entries = Entry.query.filter(
                Entry.user_id == user_id,
                Entry.entry_date >= start_date,
                Entry.entry_date <= end_date
            ).limit(limit).all()
            
            # Fallback to created_at if no entries found
            if not entries:
                entries = Entry.query.filter(
                    Entry.user_id == user_id,
                    db.func.date(Entry.created_at) >= start_date,
                    db.func.date(Entry.created_at) <= end_date
                ).limit(limit).all()
            
            return entries
            
        except Exception as e:
            print(f"❌ Date-only search failed: {e}")
            return []
    
    @staticmethod
    def _parse_dates_from_query(query: str) -> Optional[Tuple[date, date]]:
        """Parse date ranges from natural language query using regex patterns"""
        try:
            import re
            from datetime import timedelta
            import calendar
            
            query_lower = query.lower()
            today = datetime.now().date()
            
            # Relative date patterns
            if re.search(r'\b(current month|this month)\b', query_lower):
                start_date = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end_date = today.replace(day=last_day)
                return start_date, end_date
                
            elif re.search(r'\b(last month|previous month)\b', query_lower):
                if today.month == 1:
                    prev_month, prev_year = 12, today.year - 1
                else:
                    prev_month, prev_year = today.month - 1, today.year
                start_date = date(prev_year, prev_month, 1)
                last_day = calendar.monthrange(prev_year, prev_month)[1]
                end_date = date(prev_year, prev_month, last_day)
                return start_date, end_date
                
            elif re.search(r'\b(this week|current week)\b', query_lower):
                days_since_monday = today.weekday()
                start_date = today - timedelta(days=days_since_monday)
                end_date = start_date + timedelta(days=6)
                return start_date, end_date
                
            elif re.search(r'\b(last week|previous week)\b', query_lower):
                days_since_monday = today.weekday()
                this_monday = today - timedelta(days=days_since_monday)
                start_date = this_monday - timedelta(days=7)
                end_date = start_date + timedelta(days=6)
                return start_date, end_date
            
            # Specific date patterns (simplified - add more as needed)
            month_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
                'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
                'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
            }
            
            # Match "August 2025" or "aug 2025" patterns
            month_year_pattern = r'\b(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\s+(\d{4})\b'
            match = re.search(month_year_pattern, query_lower)
            if match:
                month_name, year_str = match.groups()
                month_num = month_map.get(month_name.lower())
                year = int(year_str)
                if month_num:
                    start_date = date(year, month_num, 1)
                    last_day = calendar.monthrange(year, month_num)[1]
                    end_date = date(year, month_num, last_day)
                    return start_date, end_date
            
            return None
            
        except Exception as e:
            print(f"❌ Date parsing failed: {e}")
            return None

    # Legacy compatibility methods (delegate to unified search)
    @staticmethod
    def find_similar_entries(embedding: List[float], user_id: int, limit: int = 10) -> List[Entry]:
        """Legacy method - delegates to unified search"""
        return DatabaseService.search_entries(user_id=user_id, embedding=embedding, limit=limit)
    
    @staticmethod
    def find_entries_by_date_query(query: str, user_id: int) -> List[Entry]:
        """Legacy method - delegates to unified search"""
        return DatabaseService.search_entries(user_id=user_id, query=query)
    
    @staticmethod
    def find_entries_by_month_range(user_id: int, year: int, month: int) -> List[Entry]:
        """Legacy method - delegates to unified search"""
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        return DatabaseService.search_entries(
            user_id=user_id, start_date=start_date, end_date=end_date
        )
    
    @staticmethod
    def find_similar_entries_with_date_filter(embedding: List[float], user_id: int, 
                                            start_date=None, end_date=None, limit: int = 10) -> List[Entry]:
        """Legacy method - delegates to unified search"""
        return DatabaseService.search_entries(
            user_id=user_id, embedding=embedding, start_date=start_date, 
            end_date=end_date, limit=limit
        )
    
    @staticmethod
    def find_similar_entries_with_llm_date_filter(embedding: List[float], user_id: int, 
                                                  date_filter: Dict[str, Any] = None, limit: int = 10) -> List[Entry]:
        """Legacy method - delegates to unified search"""
        return DatabaseService.search_entries(
            user_id=user_id, embedding=embedding, date_filter=date_filter, limit=limit
        )
    
    @staticmethod
    def find_entries_by_llm_date_filter(user_id: int, date_filter: Dict[str, Any]) -> List[Entry]:
        """Legacy method - delegates to unified search"""
        return DatabaseService.search_entries(user_id=user_id, date_filter=date_filter)
    
    # Utility methods
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