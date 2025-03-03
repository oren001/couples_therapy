from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key != "your_openai_api_key_here":
    openai.api_key = api_key
    print(f"OpenAI API key loaded successfully: {api_key[:4]}...{api_key[-4:]}")
else:
    print("No valid OpenAI API key found. Using simulated responses.")
    openai.api_key = None

app = Flask(__name__)
# Enable CORS for all routes with more specific settings
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

# In-memory storage for conversation history
partner1_conversation = []
partner2_conversation = []
therapist_conversation = []

@app.route('/')
def home():
    return jsonify({"message": "Hello from the Couples Therapy API"})

@app.route('/test')
def test():
    return jsonify({"status": "API is working correctly"})

@app.route('/partner/1/message', methods=['POST', 'OPTIONS'])
def partner1_message():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
        return response
        
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Add message to partner 1's conversation
    partner1_conversation.append({"role": "user", "content": message})
    
    # Get response from representor
    try:
        response = get_representor_response(message, 1)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in partner1_message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/partner/2/message', methods=['POST', 'OPTIONS'])
def partner2_message():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
        return response
        
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Add message to partner 2's conversation
    partner2_conversation.append({"role": "user", "content": message})
    
    # Get response from representor
    try:
        response = get_representor_response(message, 2)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in partner2_message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/partner/1/approve', methods=['POST', 'OPTIONS'])
def partner1_approve():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
        return response
        
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Add approved message to therapist conversation
    therapist_conversation.append({"role": "user", "content": f"Partner 1: {message}"})
    
    # Get response from therapist
    try:
        response = get_therapist_response(message, 1)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in partner1_approve: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/partner/2/approve', methods=['POST', 'OPTIONS'])
def partner2_approve():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
        return response
        
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Add approved message to therapist conversation
    therapist_conversation.append({"role": "user", "content": f"Partner 2: {message}"})
    
    # Get response from therapist
    try:
        response = get_therapist_response(message, 2)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in partner2_approve: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/conversation/history', methods=['GET'])
def get_conversation_history():
    return jsonify({
        "partner1": partner1_conversation,
        "partner2": partner2_conversation,
        "therapist": therapist_conversation
    })

def get_representor_response(message, partner_id):
    """Get a response from the representor LLM for the specified partner."""
    conversation = partner1_conversation if partner_id == 1 else partner2_conversation
    
    # Limit conversation history to last 10 messages
    recent_conversation = conversation[-10:] if len(conversation) > 10 else conversation
    
    # Create system message for the representor
    system_message = {
        "role": "system",
        "content": f"You are a helpful representor for Partner {partner_id} in a couples therapy session. "
                   f"Your goal is to help them express their thoughts and feelings in a constructive way. "
                   f"Suggest improvements to their message that maintain their core meaning but phrase it "
                   f"in a way that is more likely to be received well by their partner."
    }
    
    # Prepare messages for the API call
    messages = [system_message] + recent_conversation
    
    try:
        # For testing without API calls
        if not openai.api_key or openai.api_key == "your_openai_api_key_here":
            print(f"Using simulated response for Partner {partner_id}")
            response_text = f"This is a simulated response from the representor for Partner {partner_id}. "
            response_text += "I suggest phrasing your message like this: " + message
            
            # Add response to conversation
            conversation.append({"role": "assistant", "content": response_text})
            return response_text
        
        print(f"Making API call to OpenAI for Partner {partner_id}")
        # Make API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        response_text = response.choices[0].message.content
        
        # Add response to conversation
        conversation.append({"role": "assistant", "content": response_text})
        
        return response_text
    except Exception as e:
        print(f"Error in get_representor_response: {str(e)}")
        return f"Error: {str(e)}"

def get_therapist_response(message, partner_id):
    """Get a response from the therapist LLM."""
    # Limit conversation history to last 15 messages
    recent_conversation = therapist_conversation[-15:] if len(therapist_conversation) > 15 else therapist_conversation
    
    # Create system message for the therapist
    system_message = {
        "role": "system",
        "content": "You are a skilled couples therapist. Your goal is to mediate between both partners, "
                   "help them understand each other's perspectives, and guide them toward resolution. "
                   "Provide thoughtful, balanced responses that acknowledge both sides."
    }
    
    # Prepare messages for the API call
    messages = [system_message] + recent_conversation
    
    try:
        # For testing without API calls
        if not openai.api_key or openai.api_key == "your_openai_api_key_here":
            print(f"Using simulated response from therapist for Partner {partner_id}")
            response_text = "This is a simulated response from the therapist. "
            response_text += f"I understand Partner {partner_id}'s perspective. Let me help facilitate communication between both partners."
            
            # Add response to conversation
            therapist_conversation.append({"role": "assistant", "content": response_text})
            return response_text
        
        print(f"Making API call to OpenAI for therapist response")
        # Make API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        response_text = response.choices[0].message.content
        
        # Add response to conversation
        therapist_conversation.append({"role": "assistant", "content": response_text})
        
        return response_text
    except Exception as e:
        print(f"Error in get_therapist_response: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    print("Starting Couples Therapy API server...")
    print("API will be available at http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000, debug=True) 