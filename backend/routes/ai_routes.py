from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.llm_service import llm_service
from services.database_service import DatabaseService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/search', methods=['POST'])
@jwt_required()
def ai_search():
    try:
        user_id = int(get_jwt_identity())  # Convert to int
        data = request.get_json()
        
        if not data or not data.get('query'):
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        print(f"🔍 AI Search Request - User: {user_id}, Query: '{query}'")
        
        # Step 1: Extract date filter using LLM
        print("🤖 Extracting date filter using LLM...")
        date_filter = llm_service.extract_date_filter(query)
        print(f"📅 LLM Date Filter Result: {date_filter}")
        
        # Step 2: Generate embedding for the search query
        query_embedding = None
        try:
            query_embedding = llm_service.generate_embedding(query)
            print(f"🧠 Generated embedding of length {len(query_embedding) if query_embedding else 0}")
        except Exception as e:
            print(f"Warning: Could not generate search embedding: {str(e)}")
            # Fall back to basic text search
            return jsonify({
                'response': "AI search is currently unavailable. Please try again later or use the basic search feature.",
                'relevant_entries_count': 0,
                'ai_available': False
            }), 200

        # Step 3: Search entries with LLM-extracted date filter
        relevant_entries = []
        
        if date_filter.get('has_date_filter'):
            print(f"🔍 Using LLM date-filtered search...")
            # Use LLM date-filtered vector search
            relevant_entries = DatabaseService.find_similar_entries_with_llm_date_filter(
                embedding=query_embedding,
                user_id=user_id,
                date_filter=date_filter,
                limit=10
            )
            print(f"📅 LLM date-filtered search found {len(relevant_entries)} entries")
            
            # If no entries found via embedding with date filter, try pure date search
            if not relevant_entries:
                print("🔄 Falling back to pure LLM date search...")
                relevant_entries = DatabaseService.find_entries_by_llm_date_filter(user_id, date_filter)
                print(f"� Pure LLM date search found {len(relevant_entries)} entries")
        else:
            print(f"🔍 No date filter detected, using regular vector search...")
            # No date filtering, use regular vector search
            relevant_entries = DatabaseService.find_similar_entries(
                embedding=query_embedding,
                user_id=user_id,
                limit=10
            )
            print(f"🔎 Regular vector search found {len(relevant_entries)} entries")
            
            # Fallback to old regex-based date search if no results
            if not relevant_entries:
                print("🔄 Falling back to regex date search...")
                relevant_entries = DatabaseService.find_entries_by_date_query(query, user_id)
                print(f"📅 Regex date search found {len(relevant_entries)} entries")
        
        if not relevant_entries:
            return jsonify({
                'response': "I couldn't find any relevant entries to answer your question. Try adding more journal entries first!",
                'relevant_entries_count': 0,
                'ai_available': True
            }), 200
        
        # Prepare context from relevant entries (optimized for fewer tokens)
        context_entries = []
        for entry in relevant_entries:
            # Use entry_date if available, fallback to created_at
            entry_date_str = entry.entry_date.strftime('%m-%d') if entry.entry_date else entry.created_at.strftime('%m-%d')
            # Compact format: just date and content, no labels
            context_entries.append(f"{entry_date_str}: {entry.content}")
        
        context = "\n\n".join(context_entries)

        print(context)
        
        # Create prompt for the LLM (optimized for fewer tokens)
        prompt = f"""Answer based on these journal entries. Be conversational and mention dates when relevant.

Entries:
{context}

Question: {query}

Answer:"""
        
        # Generate response using LLM
        try:
            response = llm_service.generate_text(prompt)
        except Exception as e:
            print(f"Warning: Could not generate AI response: {str(e)}")
            return jsonify({
                'response': "I found relevant entries but couldn't generate a response due to AI service issues. Please try again later.",
                'relevant_entries_count': len(relevant_entries),
                'ai_available': False
            }), 200
        
        return jsonify({
            'response': response,
            'relevant_entries_count': len(relevant_entries),
            'ai_available': True
        }), 200
        
    except Exception as e:
        print(f"Error in AI search: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your search'}), 500

@ai_bp.route('/search/test', methods=['GET'])
@jwt_required()
def test_ai_search():
    """Test endpoint to verify AI service is working"""
    try:
        # Simple test of the LLM service
        test_response = llm_service.generate_text("Say hello!")
        test_embedding = llm_service.generate_embedding("This is a test.")
        
        return jsonify({
            'message': 'AI service is working',
            'test_response': test_response,
            'embedding_length': len(test_embedding) if test_embedding else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'AI service error: {str(e)}'}), 500
