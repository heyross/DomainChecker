import openai
from flask import Flask, request, jsonify
import whois
import os
import logging
import requests
response = requests.get('http://remote-api-service:5000/api/resource')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Run all interfaces on port 5000

app.run(host='0.0.0.0', port=5000)

# Set your OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    openai.api_key = openai_api_key
else:
    raise ValueError("OPENAI_API_KEY is not set in environment variables. Please set it correctly before running the app.")

# List of TLDs to check
tlds = ['.com', '.org', '.net', '.io']

# Custom error handler for catching unexpected errors
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"An unexpected error occurred: {str(e)}")
    return jsonify({
        "error": "An unexpected error occurred.",
        "details": str(e)
    }), 500

# WHOIS lookup function
def check_whois(domain):
    try:
        logging.info(f"Checking WHOIS for domain: {domain}")
        domain_info = whois.whois(domain)
        if domain_info['domain_name']:
            return 'Registered'
    except Exception as e:
        logging.error(f"Error checking WHOIS for {domain}: {e}")
        return 'Error'
    return 'Available'

# Function to generate company names using GPT
def generate_company_names(description):
    logging.info(f"Received prompt for description: {description}")

    prompt = f"""
    Generate a set of company name candidates that evoke a symbolic connection...
    """

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        generated_text = response.choices[0].text.strip()
        logging.info(f"OpenAI API response: {generated_text}")

        # Evaluate the generated text into a Python list if the response is valid Python code
        try:
            exec(generated_text, globals())
        except Exception as exec_error:
            logging.error(f"Error executing the generated Python code: {exec_error}")
            return None, f"Error processing OpenAI API response: {exec_error}"

        logging.info(f"Generated names: {names}")
        return names
    except Exception as e:
        logging.error(f"Error in OpenAI API call: {e}")
        return None, f"An error occurred while communicating with the OpenAI API: {e}"

# Route to generate names
@app.route('/generate_names', methods=['POST'])
def generate_names():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")

        if 'description' not in data or not data['description'].strip():
            return jsonify({'error': "The 'description' field is missing or empty."}), 400

        description = data['description']
        names, error = generate_company_names(description)

        if error:
            logging.error(f"Error generating names: {error}")
            return jsonify({'error': error}), 500

        response = {'names': names}
        logging.info(f"Sending response: {response}")
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in /generate_names route: {e}")
        return jsonify({"error": "An error occurred while processing your request.", "details": str(e)}), 500

# Route to check domain
@app.route('/check_domain', methods=['POST'])
def check_domain():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")

        if 'name' not in data or 'tld' not in data:
            return jsonify({'error': "Both 'name' and 'tld' fields are required to check a domain."}), 400

        name = data['name']
        tld = data['tld']
        domain = f"{name}{tld}"

        status = check_whois(domain)
        response = {'domain': domain, 'status': status}
        logging.info(f"Sending response: {response}")
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in /check_domain route: {e}")
        return jsonify({"error": "An error occurred while checking the domain.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
