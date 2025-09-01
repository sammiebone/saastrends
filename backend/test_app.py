import unittest
from unittest.mock import patch
import json
from app import app, db, TrackedKeyword

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

class TrendsApiTestCase(BaseTestCase):
    @patch('app.get_rising_queries')
    def test_content_ideas_success(self, mock_get_rising_queries):
        mock_get_rising_queries.return_value = [{'query': 'ai in marketing', 'value': 150}]
        response = self.app.get('/api/content-ideas?topic=AI')
        self.assertEqual(response.status_code, 200)
        mock_get_rising_queries.assert_called_once_with(keyword='AI', timeframe='today 3-m', geo='', cat=0, gprop='')

    @patch('app.get_trending_searches')
    def test_trending_topics_success(self, mock_get_trending_searches):
        mock_get_trending_searches.return_value = ['SaaS', 'AI', 'Fintech']
        response = self.app.get('/api/trending-topics?pn=japan')
        self.assertEqual(response.status_code, 200)
        mock_get_trending_searches.assert_called_once_with(pn='japan')

class KeywordApiTestCase(BaseTestCase):
    def test_add_keyword(self):
        response = self.app.post('/api/keywords',
                                 data=json.dumps({'keyword': 'SaaS'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('SaaS', str(response.data))
        with app.app_context():
            self.assertEqual(TrackedKeyword.query.count(), 1)

    def test_get_keywords(self):
        with app.app_context():
            db.session.add(TrackedKeyword(keyword='AI'))
            db.session.commit()

        response = self.app.get('/api/keywords')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['keyword'], 'AI')

    def test_delete_keyword(self):
        with app.app_context():
            kw = TrackedKeyword(keyword='Fintech')
            db.session.add(kw)
            db.session.commit()
            keyword_id = kw.id

        delete_response = self.app.delete(f'/api/keywords/{keyword_id}')
        self.assertEqual(delete_response.status_code, 200)

        with app.app_context():
            self.assertEqual(TrackedKeyword.query.count(), 0)

    @patch('app.get_interest_over_time')
    def test_get_keyword_interest(self, mock_get_interest):
        mock_get_interest.return_value = [{'date': '2023-01-01', 'SaaS': 100}]

        with app.app_context():
            kw = TrackedKeyword(keyword='SaaS')
            db.session.add(kw)
            db.session.commit()
            keyword_id = kw.id

        interest_response = self.app.get(f'/api/keywords/{keyword_id}/interest')
        self.assertEqual(interest_response.status_code, 200)
        data = json.loads(interest_response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['SaaS'], 100)
        mock_get_interest.assert_called_once_with(keywords=['SaaS'])

if __name__ == '__main__':
    unittest.main()
