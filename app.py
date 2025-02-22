import openai
from flask import Flask, request, jsonify, render_template, redirect, url_for
import whois
import os
import logging
import requests
import sys
import argparse

response = requests.get('http://remote-api-service:5000/api/resource')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Run all interfaces on port 5000

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

# Function to generate company names using Ollama LLM
def generate_company_names_with_ollama(input_text):
    try:
        # Assuming Ollama service is running on localhost:8000
        url = 'http://localhost:8000/generate'
        headers = {'Content-Type': 'application/json'}
        data = {'input': input_text, 'use_gpu': True}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('generated_names', [])
    except Exception as e:
        logging.error(f"Error generating names with Ollama LLM: {e}")
        return []

# Function to generate company names using GPT
def generate_company_names(description):
    return generate_company_names_with_ollama(description)

# Function to check domain availability using Namecheap API
def check_domain_availability(domain):
    api_key = os.getenv('NAMECHEAP_API_KEY')
    url = f'https://api.namecheap.com/xml.response?ApiUser=yourApiUser&ApiKey={api_key}&UserName=yourUserName&Command=namecheap.domains.check&ClientIp=yourClientIp&DomainList={domain}'
    try:
        response = requests.get(url)
        # Parse the XML response to check availability
        if '<Available>true</Available>' in response.text:
            return 'Available'
        else:
            return 'Not Available'
    except Exception as e:
        logging.error(f"Error checking domain availability with Namecheap: {e}")
        return 'Error'

# Route to generate names
@app.route('/generate_names', methods=['POST'])
def generate_names():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")

        if 'description' not in data or not data['description'].strip():
            return jsonify({'error': "The 'description' field is missing or empty."}), 400

        description = data['description']
        names = generate_company_names(description)

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    description = request.form['description']
    names = generate_company_names(description)
    return render_template('index.html', generated_names=names)

@app.route('/check', methods=['POST'])
def check():
    domain = request.form['domain']
    status = check_whois(domain)
    return render_template('index.html', domain_status=status)

# Command-line interface setup
parser = argparse.ArgumentParser(description='DomainChecker CLI')
parser.add_argument('--generate', type=str, help='Generate company names based on a description')
parser.add_argument('--check', type=str, help='Check domain availability')
args = parser.parse_args()

if args.generate:
    description = args.generate
    print(f"Generating company names for description: {description}")
    # Call the generate_company_names function and print results
    names = generate_company_names(description)
    print("Generated names:", names)

if args.check:
    domain = args.check
    print(f"Checking availability for domain: {domain}")
    # Call the check_whois function and print result
    status = check_whois(domain)
    print(f"Domain {domain} is {status}")

# Run the Flask app only if no CLI arguments are provided
if not (args.generate or args.check):
    app.run(debug=True)
