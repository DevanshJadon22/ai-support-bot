# import os
# import json
# # Make sure you have the openai library installed: pip3 install openai
# from openai import OpenAI
# from .models import db, ChatSession, Message
# client = OpenAI()

# # --- Setup ---
# # It's best practice to load your API key from an environment variable
# # We will set this up in the next step.
# # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# def load_faqs():
#     """Loads the FAQ data from the JSON file."""
#     with open('faqs.json', 'r') as f:
#         return json.load(f)

# FAQ_DATA = load_faqs()
# # We format the FAQs into a single string to pass to the LLM
# FAQ_CONTEXT = " ".join([f"Question: {item['question']} Answer: {item['answer']}" for item in FAQ_DATA])

# # --- Database Functions ---
# def create_new_session():
#     """Creates and saves a new chat session."""
#     new_session = ChatSession()
#     db.session.add(new_session)
#     db.session.commit()
#     return new_session

# def get_conversation_history(session_id):
#     """Retrieves conversation history for contextual memory."""
#     messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()
#     # Format for the LLM API
#     history = [{"role": msg.role, "content": msg.content} for msg in messages]
#     return history

# def summarize_conversation(history):
#     """Generates a summary for escalation. (Placeholder for now)"""
#     user_questions = [msg['content'] for msg in history if msg['role'] == 'user']
#     return f"User asked about: {', '.join(user_questions)}. The bot was unable to resolve the final query."

# # --- Core LLM Logic ---
# def get_llm_response(session_id, user_query):
#     """Main function to get a response from the LLM."""
#     # 1. Save the user's new message to the database
#     user_message = Message(session_id=session_id, role="user", content=user_query)
#     db.session.add(user_message)
#     db.session.commit()

#     # 2. Get the entire conversation history
#     history = get_conversation_history(session_id)

#     # 3. Construct the prompt for the LLM
#     # This is a critical step in prompt engineering.
#     system_prompt = f"""
#     You are a helpful AI customer support bot.
#     Your knowledge base is strictly limited to the following FAQs.
#     Answer the user's question based ONLY on this information.
#     If the question cannot be answered using the provided FAQs, you MUST respond with the exact phrase "ESCALATE".
#     Do not add any extra information or apologies. Just say "ESCALATE".

#     <FAQs>
#     {FAQ_CONTEXT}
#     </FAQs>
#     """
    
#     messages_for_llm = [{"role": "system", "content": system_prompt}] + history

#     # --- THIS IS A PLACEHOLDER - WE WILL REPLACE IT IN THE NEXT STEP ---
#     # To test the flow, we'll use simple logic instead of a real API call.
#     # if "password" in user_query.lower():
#     #     assistant_response = "You can reset your password by clicking the 'Forgot Password' link on the login page."
#     # elif "hours" in user_query.lower():
#     #     assistant_response = "Our business hours are from 9 AM to 6 PM, Monday to Friday."
#     # else:
#     #     assistant_response = "ESCALATE" # Simulate escalation
#     # --- Real LLM API Call ---
#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",        # A popular and cost-effective model
#             messages=messages_for_llm,   # The prompt and conversation history
#             temperature=0.1              # A low temperature makes the output more focused and deterministic
#         )
#         assistant_response = response.choices[0].message.content.strip()
#     except Exception as e:
#         # If the API call fails for any reason, print the error and escalate
#         print(f"An error occurred with the OpenAI API: {e}")
#         assistant_response = "ESCALATE"
#     # --- End of API Call ---
#     # --- END OF PLACEHOLDER ---
        
#     # 4. Handle Escalation
#     if assistant_response == "ESCALATE":
#         summary = summarize_conversation(history)
#         session = ChatSession.query.get(session_id)
#         session.summary = summary # Save summary to the database
#         db.session.commit()
        
#         response_data = {
#             "response": "I'm sorry, I can't answer that question. I will escalate this to a human agent.",
#             "status": "escalated",
#             "summary": summary
#         }
#     else:
#         # 5. Save the assistant's response to the database
#         assistant_message = Message(session_id=session_id, role="assistant", content=assistant_response)
#         db.session.add(assistant_message)
#         db.session.commit()
#         response_data = {"response": assistant_response, "status": "answered"}

#     return response_data
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from .models import db, ChatSession, Message

# Load variables from .env file
load_dotenv()

# Configure the Gemini client with the API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def load_faqs():
    """Loads the FAQ data from the JSON file."""
    with open('faqs.json', 'r') as f:
        return json.load(f)

FAQ_DATA = load_faqs()
FAQ_CONTEXT = " ".join([f"Question: {item['question']} Answer: {item['answer']}" for item in FAQ_DATA])

# --- Database Functions (No changes here) ---
def create_new_session():
    """Creates and saves a new chat session."""
    new_session = ChatSession()
    db.session.add(new_session)
    db.session.commit()
    return new_session

def get_conversation_history(session_id):
    """Retrieves conversation history for contextual memory."""
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()
    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    return history

def summarize_conversation(history):
    """Generates a summary for escalation."""
    user_questions = [msg['content'] for msg in history if msg['role'] == 'user']
    return f"User asked about: {', '.join(user_questions)}. The bot was unable to resolve the final query."

# --- Core LLM Logic (Updated for Gemini) ---
def get_llm_response(session_id, user_query):
    """Main function to get a response from the Gemini model."""
    user_message = Message(session_id=session_id, role="user", content=user_query)
    db.session.add(user_message)
    db.session.commit()

    history = get_conversation_history(session_id)

    system_prompt = f"""
    You are an AI customer support bot. Your primary goal is to answer user questions based on the provided FAQs.
    Carefully read the FAQs below. If the user's question can be answered using this information, provide the answer directly from the text.
    If the question absolutely cannot be answered from the FAQs, you must respond with the exact phrase "ESCALATE".

    <FAQs>
    {FAQ_CONTEXT}
    </FAQs>
    """
    
    # Gemini requires a slightly different message format and history structure
    # We combine the system prompt and history into a single list
    messages_for_gemini = [{"role": "user", "parts": [system_prompt]}]
    # Gemini uses 'model' for the assistant's role, so we convert it
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        messages_for_gemini.append({"role": role, "parts": [msg["content"]]})

    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-pro')
        # Start a chat session with the full history
        chat = model.start_chat(history=messages_for_gemini[:-1]) # History excluding the last user message
        # Send the latest user message
        response = chat.send_message(messages_for_gemini[-1]["parts"])
        assistant_response = response.text.strip()
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        assistant_response = "ESCALATE"
        
    if "ESCALATE" in assistant_response:
        summary = summarize_conversation(history)
        session = ChatSession.query.get(session_id)
        session.summary = summary
        db.session.commit()
        
        response_data = {
            "response": "I'm sorry, I can't answer that question. I will escalate this to a human agent.",
            "status": "escalated",
            "summary": summary
        }
    else:
        assistant_message = Message(session_id=session_id, role="assistant", content=assistant_response)
        db.session.add(assistant_message)
        db.session.commit()
        response_data = {"response": assistant_response, "status": "answered"}

    return response_data