import openai
from flask import Flask, request, jsonify
import time
import os

# Initialize the Flask app
app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

# List of TLDs to check
tlds = ['.com', '.org', '.net', '.io', '.info', '.biz', '.co', '.us', '.uk', '.me']

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
        # Execute the generated code to convert it into a Python list
        exec(generated_text, globals())
        return names  # Return the generated list of names
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return []

@app.route('/check_domains', methods=['POST'])
def check_domains():
    data = request.get_json()
    description = data.get('description')

    # Generate company names using GPT-4
    domain_ideas = generate_company_names(description)

    results = []
    for name in domain_ideas:
        for tld in tlds:
            domain = f"{name}{tld}"
            status = check_whois(domain)
            results.append({'domain': domain, 'status': status})
            time.sleep(1)  # Respect WHOIS server rate limits

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)
