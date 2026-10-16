import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app

class ApiTests(unittest.TestCase):
    def setUp(self): self.client=TestClient(app)
    def test_health(self): self.assertEqual(self.client.get('/health').status_code, 200)
    def test_summary_shape(self):
        body=self.client.get('/api/summary').json()
        self.assertIn('objects', body); self.assertIn('screening_runs', body)
    def test_pagination_and_errors(self):
        response=self.client.get('/api/objects?limit=2&offset=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)
        self.assertIn('total', response.json())
        self.assertEqual(self.client.get('/api/objects/999999').status_code, 404)
        self.assertEqual(self.client.get('/api/objects?limit=0').status_code, 422)
    def test_eda_and_candidates_schema(self):
        self.assertEqual(self.client.get('/api/eda').status_code, 200)
        body=self.client.get('/api/close-approaches').json()
        self.assertEqual(body['count'], len(body['items']))

if __name__ == '__main__': unittest.main()
