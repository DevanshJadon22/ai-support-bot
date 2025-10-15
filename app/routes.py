from flask import request, jsonify
from flask import current_app as app
from .models import db, ChatSession
# from .services import get_llm_response, create_new_session
# AFTER
from .services import get_llm_response
from .models import create_new_session

@app.route('/session', methods=['POST'])
def start_session():
    """Endpoint to create a new chat session."""
    session = create_new_session()
    return jsonify({"session_id": session.id}), 201

@app.route('/chat', methods=['POST'])
def chat():
    """Main endpoint to handle customer queries."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    session_id = data.get('session_id')
    user_query = data.get('query')

    if not session_id or not user_query:
        return jsonify({"error": "session_id and query are required"}), 400

    # Check if the session exists
    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Invalid session_id"}), 404

    # Get the response from our core logic in services.py
    response_data = get_llm_response(session_id, user_query)
    
    return jsonify(response_data)