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
        
        # Try to generate embedding for the search query
        query_embedding = None
        try:
            query_embedding = llm_service.generate_embedding(query)
        except Exception as e:
            print(f"Warning: Could not generate search embedding: {str(e)}")
            # Fall back to basic text search
            return jsonify({
                'response': "AI search is currently unavailable. Please try again later or use the basic search feature.",
                'relevant_entries_count': 0,
                'ai_available': False
            }), 200
        
        # Find similar entries using vector search
        relevant_entries = DatabaseService.find_similar_entries(
            embedding=query_embedding,
            user_id=user_id,
            limit=10
        )
        
        # If no entries found via embedding, try date-based search
        if not relevant_entries:
            relevant_entries = DatabaseService.find_entries_by_date_query(query, user_id)
        
        if not relevant_entries:
            return jsonify({
                'response': "I couldn't find any relevant entries to answer your question. Try adding more journal entries first!",
                'relevant_entries_count': 0,
                'ai_available': True
            }), 200
        
        # Prepare context from relevant entries
        context_entries = []
        for entry in relevant_entries:
            # Use entry_date if available, fallback to created_at
            entry_date_str = entry.entry_date.strftime('%Y-%m-%d') if entry.entry_date else entry.created_at.strftime('%Y-%m-%d')
            context_entries.append(f"Date: {entry_date_str}\nContent: {entry.content}")
        
        context = "\n\n---\n\n".join(context_entries)
        
        # Create prompt for the LLM
        prompt = f"""Based on the following journal entries, please answer the user's question in a conversational and helpful manner. Provide specific details from the entries when relevant, and mention dates when appropriate.

Journal Entries:
{context}

User's Question: {query}

Please provide a concise, summary-style answer that directly addresses the question:"""
        
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
