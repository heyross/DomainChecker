import whois
from whois import whois
import time

# List of names to check
names = [
    'Beacon', 'Talon', 'Seraph', 'Vigil', 'Rune', 'Shepherd', 'Lumen', 
    'Atlas', 'Sentient', 'Nimbus', 'Arcane', 'Solace', 'Codex', 'Verity', 
    'Zephyr', 'Halcyon', 'Covenant', 'Sentinel', 'Oracle', 'Haven', 'Dominion', 
    'Radiant', 'Axiom', 'Keystone', 'Exemplar', 'Paragon', 'Solara', 
    'Meridian', 'Veritas', 'Zenith', 'Wayfarer', 'Aeon', 'Templar', 
    'Quorum', 'Omnia', 'Fathom', 'Bastion', 'Ethereal', 'Obsidian', 'Sanctum'
]


# List of TLDs to explore (you can expand or adjust this list)
tlds = ['.com', '.org', '.net', '.io', '.info', '.biz', '.co', '.us', '.uk', '.me']

def check_whois(domain):
    try:
        # Perform the WHOIS lookup
        domain_info = whois(domain)
        
        # If the domain has a registrar or creation date, it likely exists
        if domain_info['domain_name']:
            return True
        return False
    except Exception as e:
        # WHOIS lookup failed, domain might be available or WHOIS server is down
        return False

# Iterate through each name and TLD combination
for name in names:
    print(f"\nChecking domains for: {name}")
    for tld in tlds:
        domain = f"{name}{tld}"
        if check_whois(domain):
            print(f"Domain exists: {domain}")
        else:
            print(f"Domain is likely available: {domain}")
        # Add a small delay to avoid overwhelming the WHOIS servers
        time.sleep(1)
