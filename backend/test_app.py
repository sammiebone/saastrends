import unittest
from unittest.mock import patch
import json
from app import app

class ApiTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client for the app."""
        self.app = app.test_client()
        self.app.testing = True

    # --- Tests for /api/content-ideas ---

    @patch('app.get_rising_queries')
    def test_content_ideas_success(self, mock_get_rising_queries):
        """Test the content ideas endpoint with a valid topic."""
        mock_get_rising_queries.return_value = [
            {'query': 'ai in marketing', 'value': 150},
            {'query': 'future of ai', 'value': 120}
        ]
        response = self.app.get('/api/content-ideas?topic=AI')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        mock_get_rising_queries.assert_called_once_with(keyword='AI', timeframe='today 3-m', geo='', cat=0, gprop='')


    def test_content_ideas_no_topic(self):
        """Test the content ideas endpoint without a topic parameter."""
        response = self.app.get('/api/content-ideas')
        self.assertEqual(response.status_code, 400)

    # --- Tests for /api/trending-topics ---

    @patch('app.get_trending_searches')
    def test_trending_topics_success(self, mock_get_trending_searches):
        """Test the trending topics endpoint with a specific country."""
        mock_get_trending_searches.return_value = ['SaaS', 'AI', 'Fintech']
        response = self.app.get('/api/trending-topics?pn=japan')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, ['SaaS', 'AI', 'Fintech'])
        mock_get_trending_searches.assert_called_once_with(pn='japan')

    @patch('app.get_trending_searches')
    def test_trending_topics_default_country(self, mock_get_trending_searches):
        """Test the trending topics endpoint using the default country."""
        mock_get_trending_searches.return_value = ['Tech', 'Health']
        response = self.app.get('/api/trending-topics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, ['Tech', 'Health'])
        # Asserts that the service was called with the default 'united_states'
        mock_get_trending_searches.assert_called_once_with(pn='united_states')

if __name__ == '__main__':
    unittest.main()
