import unittest
import time
from src.hello import app  # passe den Import an deinen app-Dateinamen an

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def test_hello_endpoint_success(self):
        """Test the /api/hello endpoint returns correct data."""
        response = self.client.get('/api/hello', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_api_response_time(self):
        """Test that API responds within acceptable time limit."""
        start = time.time()
        self.client.get('/api/hello', headers=self.headers)
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0)

if __name__ == '__main__':
    unittest.main()
