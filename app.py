import openai
from flask import Flask, request, jsonify
import whois
import time
import os

app = Flask(__name__)

# Set your OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    openai.api_key = openai_api_key
else:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# List of TLDs to check
tlds = ['.com', '.org', '.net', '.io']

def check_whois(domain):
    try:
        # Perform WHOIS lookup
        domain_info = whois.whois(domain)
        if domain_info['domain_name']:
            return 'Registered'
    except:
        return 'Available'
    return 'Available'

def generate_company_names(description):
    # Define the prompt that will be passed to GPT-4
    prompt = f"""
    Generate a set of company name candidates that evoke a symbolic connection and fit Latin/Germanic language structures, inspired by literature or other symbolic sources (such as a Bible verse where God tracks every sparrow, but avoid using 'sparrow'). The company develops a software platform that tracks every learning and delivery event for an extended team, building profiles to assign the right person to the right job in projects. Prioritize one-word names that are imaginative, memorable, and suggest leadership, knowledge, guidance, or skill mastery. The names should also have high potential for driving traffic if available as .com domain names. Examples include names like 'Vigil' for watchfulness or 'Lumen' for enlightenment. Output the names in a Python list format, for example: names = ['example', 'testdomain', 'mywebsite'].
    """

    try:
        # Call the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use GPT-4 or Davinci model
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        # Extract the generated Python list from the response
        generated_text = response.choices[0].text.strip()
        exec(generated_text, globals())
        return names  # Return the generated list of names
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return []

@app.route('/generate_names', methods=['POST'])
def generate_names():
    data = request.get_json()
    description = data.get('description')

    # Generate company names using GPT-4
    names = generate_company_names(description)

    return jsonify({'names': names})

@app.route('/check_domain', methods=['POST'])
def check_domain():
    data = request.get_json()
    name = data.get('name')
    tld = data.get('tld')
    domain = f"{name}{tld}"

    # Check the WHOIS record for the domain
    status = check_whois(domain)

    return jsonify({'domain': domain, 'status': status})

if __name__ == '__main__':
    app.run(debug=True)
