import unittest
from unittest.mock import patch
import json
from app import app

class ContentIdeaGeneratorTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client for the app."""
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.get_rising_queries')
    def test_content_ideas_success(self, mock_get_rising_queries):
        """Test the content ideas endpoint with a valid topic."""
        # Configure the mock to return a sample list of ideas
        mock_get_rising_queries.return_value = [
            {'query': 'ai in marketing', 'value': 150},
            {'query': 'future of ai', 'value': 120}
        ]

        # Make a request to the endpoint
        response = self.app.get('/api/content-ideas?topic=AI')

        # Assert the response is correct
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['query'], 'ai in marketing')

        # Assert that the mocked function was called with the correct topic
        mock_get_rising_queries.assert_called_once_with('AI')

    def test_content_ideas_no_topic(self):
        """Test the content ideas endpoint without a topic parameter."""
        response = self.app.get('/api/content-ideas')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "A 'topic' query parameter is required.")

    @patch('app.get_rising_queries')
    def test_content_ideas_no_results(self, mock_get_rising_queries):
        """Test the content ideas endpoint when no results are found."""
        mock_get_rising_queries.return_value = []

        response = self.app.get('/api/content-ideas?topic=obscuretopic')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
        mock_get_rising_queries.assert_called_once_with('obscuretopic')

if __name__ == '__main__':
    unittest.main()
