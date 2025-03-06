from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configure Gemini API
api_key = 'AIzaSyAG_dEEY9pk4B2tHsPVaeX4uULqNvjatak'
try:
    genai.configure(api_key=api_key)
    logging.info("Gemini API configured successfully.")
except Exception as e:
    logging.error(f"Failed to configure Gemini API: {str(e)}")

# Initialize model
try:
    available_models = list(genai.list_models())  # Convert generator to list
    logging.info(f"Raw response from list_models: {available_models}")  # Log raw response
    if not available_models:
        logging.error("No models returned by the API. Please check your API key and permissions.")
        raise Exception("No models available.")

    # Log detailed information about each model
    for model_info in available_models:
        logging.info(f"Model Name: {model_info.name}, Supported Methods: {model_info.supported_generation_methods}")

    # Dynamically select the best available version of the 'gemini-1.5-flash' model
    preferred_model_prefix = 'models/gemini-1.5-flash'
    selected_model = None
    for model_info in available_models:
        if model_info.name.startswith(preferred_model_prefix) and 'generateContent' in model_info.supported_generation_methods:
            selected_model = model_info.name
            break

    if selected_model:
        logging.info(f"Using model: {selected_model}")
        model = genai.GenerativeModel(selected_model)
    else:
        logging.error(f"No suitable version of {preferred_model_prefix} found.")
        raise Exception(f"No suitable version of {preferred_model_prefix} found.")
except Exception as e:
    logging.error(f"Failed to fetch or initialize a valid model: {str(e)}")
    model = None

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

        # Ensure model is initialized
        if not model:
            logging.error("Model is not initialized.")
            return jsonify({'error': 'Model not initialized. Please try again later.'}), 503

        # Simple direct prompt for legal questions
        prompt = f"Explain the Indian laws and penalties for: {user_question}. Include specific sections and fines if applicable."
        
        try:
            logging.info(f"Sending prompt to model: {prompt}")
            response = model.generate_content(prompt)
            if hasattr(response, 'text') and response.text:
                logging.info("Response received from model.")
                return jsonify({'response': response.text})
            else:
                logging.error("Invalid response format from model.")
                return jsonify({'error': 'Invalid response from model. Please try again.'}), 503
        except Exception as e:
            logging.error(f"Model error: {str(e)}")
            return jsonify({'error': f'Unable to generate response: {str(e)}'}), 503
            
    except Exception as e:
        logging.error(f"Request error: {str(e)}")
        return jsonify({'error': f'Unable to process request: {str(e)}'}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)