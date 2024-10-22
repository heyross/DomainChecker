import openai
from flask import Flask, request, jsonify
import whois
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Set your OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    openai.api_key = openai_api_key
else:
    raise ValueError("OPENAI_API_KEY is not set in environment variables. Please set it correctly before running the app.")

# List of TLDs to check
tlds = ['.com', '.org', '.net', '.io']

def check_whois(domain):
    try:
        # Perform WHOIS lookup
        domain_info = whois.whois(domain)
        if domain_info['domain_name']:
            return 'Registered'
    except Exception as e:
        logging.error(f"Error checking WHOIS for {domain}: {e}")
        return 'Error'
    return 'Available'

def generate_company_names(description):
    logging.info(f"Received prompt for description: {description}")

    # Define the prompt that will be passed to GPT-4
    prompt = f"""
    Generate a set of company name candidates that evoke a symbolic connection and fit Latin/Germanic language structures, inspired by literature or other symbolic sources (such as a Bible verse where God tracks every sparrow, but avoid using 'sparrow'). The company develops a software platform that tracks every learning and delivery event for an extended team, building profiles to assign the right person to the right job in projects. Prioritize one-word names that are imaginative, memorable, and suggest leadership, knowledge, guidance, or skill mastery. The names should also have high potential for driving traffic if available as .com domain names. Examples include names like 'Vigil' for watchfulness or 'Lumen' for enlightenment. Output the names in a Python list format, for example: names = ['example', 'testdomain', 'mywebsite'].
    """

    try:
        # Call the OpenAI API with the properly formatted prompt
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use GPT-4 or Davinci model
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        # Extract the generated Python list from the response
        generated_text = response.choices[0].text.strip()
        exec(generated_text, globals())
        logging.info(f"Generated names: {names}")
        return names  # Return the generated list of names
    except openai.error.InvalidRequestError as e:
        logging.error(f"OpenAI API Invalid Request Error: {e}")
        return None, "There was an issue with the OpenAI request. Please check the prompt and ensure it is correctly formatted."
    except openai.error.AuthenticationError as e:
        logging.error(f"OpenAI API Authentication Error: {e}")
        return None, "Authentication with the OpenAI API failed. Please ensure that the OpenAI API key is correctly set and valid."
    except openai.error.RateLimitError as e:
        logging.error(f"OpenAI API Rate Limit Error: {e}")
        return None, "The OpenAI API rate limit has been exceeded. Please try again later or reduce the frequency of requests."
    except Exception as e:
        logging.error(f"General Error in OpenAI API call: {e}")
        return None, "An unexpected error occurred when calling the OpenAI API. Please try again later or contact support."

@app.route('/generate_names', methods=['POST'])
def generate_names():
    data = request.get_json()

    # Validate input
    if 'description' not in data or not data['description'].strip():
        logging.error("The 'description' field is missing or empty.")
        return jsonify({'error': "The 'description' field is missing or empty. Please provide a valid description."}), 400

    description = data.get('description')

    # Generate company names using GPT-4
    names, error = generate_company_names(description)

    if error:
        logging.error(f"Error generating names: {error}")
        return jsonify({'error': error, 'suggestion': 'Please verify your input and API key, or try again later.'}), 500

    return jsonify({'names': names})

@app.route('/check_domain', methods=['POST'])
def check_domain():
    data = request.get_json()

    # Validate input
    if 'name' not in data or 'tld' not in data:
        logging.error("Both 'name' and 'tld' fields are required to check a domain.")
        return jsonify({'error': "Both 'name' and 'tld' fields are required to check a domain."}), 400

    name = data.get('name')
    tld = data.get('tld')
    domain = f"{name}{tld}"

    # Check the WHOIS record for the domain
    status = check_whois(domain)

    if status == 'Error':
        logging.error(f"Error checking domain {domain}")
        return jsonify({'error': f"Error checking domain {domain}. This could be due to WHOIS server rate limiting or an invalid domain. Please try again later."}), 500

    return jsonify({'domain': domain, 'status': status})

if __name__ == '__main__':
    app.run(debug=True)
