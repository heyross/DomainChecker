from flask import Flask, request, jsonify
import whois
import time

app = Flask(__name__)

# List of TLDs to check
tlds = ['.com', '.org', '.net', '.io', '.info', '.biz', '.co', '.us', '.uk', '.me']

def check_whois(domain):
    try:
        domain_info = whois.whois(domain)
        if domain_info['domain_name']:
            return 'Registered'
    except:
        return 'Available'
    return 'Available'

@app.route('/check_domains', methods=['POST'])
def check_domains():
    data = request.get_json()
    description = data.get('description')

    # Generate domain ideas based on description (you can expand this logic)
    domain_ideas = [description.replace(" ", "").lower()]

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
