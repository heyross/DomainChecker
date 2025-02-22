import unittest
from app import generate_company_names_with_ollama, check_domain_availability

class TestDomainChecker(unittest.TestCase):

    def test_generate_company_names_with_ollama(self):
        # Test with a sample description
        description = "Innovative tech startup"
        names = generate_company_names_with_ollama(description)
        self.assertIsInstance(names, list)
        self.assertGreater(len(names), 0, "No names generated")

    def test_check_domain_availability(self):
        # Test with a sample domain
        domain = "example.com"
        status = check_domain_availability(domain)
        self.assertIn(status, ["Available", "Not Available", "Error"], "Unexpected status")

if __name__ == '__main__':
    unittest.main()
