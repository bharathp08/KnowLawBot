from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import logging

# Update Flask app configuration
app = Flask(__name__)  # Simplified configuration for Vercel

# Configure Gemini API with safety settings
api_key = 'AIzaSyB7hDhqN9PSs52d016llUP0SmN98pOhh5U'
genai.configure(api_key=api_key)

# Initialize model with verification
try:
    model = genai.GenerativeModel('gemini-pro')
    test_response = model.generate_content("Test connection")
    if not hasattr(test_response, 'text'):
        raise Exception("Invalid model response")
    logging.info("Model initialized successfully")
except Exception as e:
    logging.error(f"Model initialization failed: {str(e)}")
    raise

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_question = request.json.get('question')
        if not user_question:
            return jsonify({'error': 'No question provided'}), 400

        # Handle greetings
        if user_question.lower().strip() in ['hello', 'hi', 'hey']:
            greeting = "Hello! I'm KnowLawBot, your Indian legal advisor. I can help you with questions about Indian laws, regulations, and legal matters. Please describe your legal concern."
            return jsonify({'response': greeting})

        # Process legal questions
        try:
            # Enhance the prompt for better context
            legal_prompt = f"""As an Indian legal expert, explain:
            1. What are the fines and penalties for {user_question}?
            2. Which laws and sections apply?
            3. What are the legal consequences?
            Please provide specific details from Indian law."""
            
            response = model.generate_content(legal_prompt)
            if not hasattr(response, 'text'):
                raise Exception("Invalid response format")
            
            return jsonify({'response': response.text})
            
        except Exception as e:
            logging.error(f"Generation error: {str(e)}")
            return jsonify({'error': 'Unable to process request. Please try again.'}), 503

    except Exception as e:
        logging.error(f"Request error: {str(e)}")
        return jsonify({'error': 'Service temporarily unavailable'}), 503

# Add route for root path
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return "Service temporarily unavailable", 503

# Add error handler for 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Page not found'}), 404

# Add error handler for 500
@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500
if __name__ == '__main__':
    app.run(debug=False)