from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
partner_model = os.getenv("PARTNER_MODEL", "gpt-3.5-turbo")
therapist_model = os.getenv("THERAPIST_MODEL", "gpt-4")

logger.info(f"Loaded API key: {'[MASKED]' + api_key[-4:] if api_key else 'None'}")
logger.info(f"Partner Model: {partner_model}")
logger.info(f"Therapist Model: {therapist_model}")

if api_key and api_key != "your_openai_api_key_here":
    try:
        openai.api_key = api_key
        # Test the API key with a simple completion
        test_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        logger.info("OpenAI API key verified successfully")
        USE_OPENAI = True
    except Exception as e:
        logger.error(f"Error validating OpenAI API key: {str(e)}")
        logger.warning("Falling back to simulated responses")
        USE_OPENAI = False
else:
    logger.warning("No valid OpenAI API key found. Using simulated responses.")
    USE_OPENAI = False

# Store conversation history
conversation_history = {
    "partner1": [],
    "partner2": [],
    "therapist": []
}

@app.route('/test')
def test():
    return jsonify({
        "status": "API is working correctly",
        "openai_enabled": USE_OPENAI,
        "partner_model": partner_model,
        "therapist_model": therapist_model
    })

@app.route('/partner/<int:partner_id>/message', methods=['POST'])
def partner_message(partner_id):
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        # Store the message in conversation history
        conversation_history[f"partner{partner_id}"].append({
            "role": "user",
            "content": message
        })
        
        if USE_OPENAI:
            try:
                # Create system message for the representor
                system_message = {
                    "role": "system",
                    "content": f"""You are a helpful representor for Partner {partner_id} in couples therapy.
                    Your goal is to help them express their thoughts and feelings constructively.
                    Suggest improvements to their message that maintain their core meaning but phrase it
                    in a way that is more likely to be received well by their partner.
                    Keep responses concise and focused on improving communication."""
                }
                
                # Get recent conversation history
                recent_messages = conversation_history[f"partner{partner_id}"][-5:]
                messages = [system_message] + recent_messages
                
                # Make API call
                response = openai.ChatCompletion.create(
                    model=partner_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150
                )
                
                response_text = response.choices[0].message.content
                logger.info(f"OpenAI response for Partner {partner_id}: {response_text}")
                
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
                
        else:
            response_text = f"This is a simulated response for Partner {partner_id}: {message}"
            
        # Store the response
        conversation_history[f"partner{partner_id}"].append({
            "role": "assistant",
            "content": response_text
        })
        
        return jsonify({"response": response_text})
        
    except Exception as e:
        logger.error(f"Error in partner_message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/partner/<int:partner_id>/approve', methods=['POST'])
def partner_approve(partner_id):
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        # Store the approved message in therapist conversation
        conversation_history["therapist"].append({
            "role": "user",
            "content": f"Partner {partner_id}: {message}"
        })
        
        if USE_OPENAI:
            try:
                # Create system message for the therapist
                system_message = {
                    "role": "system",
                    "content": """You are a skilled couples therapist with expertise in:
                    1. Active listening and validation
                    2. Conflict resolution
                    3. Emotional intelligence
                    4. Relationship dynamics
                    
                    Provide thoughtful responses that:
                    - Acknowledge both partners' perspectives
                    - Identify underlying emotions and needs
                    - Suggest constructive ways to move forward
                    - Maintain professional boundaries
                    
                    Keep responses concise and focused on improving communication."""
                }
                
                # Get recent conversation history
                recent_messages = conversation_history["therapist"][-10:]
                messages = [system_message] + recent_messages
                
                # Make API call
                response = openai.ChatCompletion.create(
                    model=therapist_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=200
                )
                
                response_text = response.choices[0].message.content
                logger.info(f"OpenAI therapist response: {response_text}")
                
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
                
        else:
            response_text = f"This is a simulated response from the therapist. I understand Partner {partner_id}'s perspective. Let me help facilitate communication between both partners."
            
        # Store the therapist's response
        conversation_history["therapist"].append({
            "role": "assistant",
            "content": response_text
        })
        
        return jsonify({"response": response_text})
        
    except Exception as e:
        logger.error(f"Error in partner_approve: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/conversation/history', methods=['GET'])
def get_conversation_history():
    return jsonify(conversation_history)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"OpenAI API {'enabled' if USE_OPENAI else 'disabled (using simulated responses)'}")
    
    app.run(host=host, port=port, debug=debug) 