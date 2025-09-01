import unittest
from unittest.mock import patch
import json
from datetime import datetime
from app import app, db, TrackedKeyword, BlogPost, PlatformIntegration
import recommendation_service

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

# ... (TrendsApiTestCase and KeywordApiTestCase from before, unchanged) ...
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
        response = self.app.post('/api/keywords', data=json.dumps({'keyword': 'SaaS'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
    def test_get_keywords(self):
        with app.app_context():
            db.session.add(TrackedKeyword(keyword='AI'))
            db.session.commit()
        response = self.app.get('/api/keywords')
        self.assertEqual(response.status_code, 200)
    def test_delete_keyword(self):
        with app.app_context():
            kw = TrackedKeyword(keyword='Fintech')
            db.session.add(kw)
            db.session.commit()
            keyword_id = kw.id
        delete_response = self.app.delete(f'/api/keywords/{keyword_id}')
        self.assertEqual(delete_response.status_code, 200)
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
    @patch('app.semrush_service.get_organic_positions')
    @patch('app.get_interest_over_time')
    def test_get_seo_dashboard_data(self, mock_get_interest, mock_get_ranks):
        mock_get_interest.return_value = [{'date': '2023-01-01', 'AI': 50}]
        mock_get_ranks.return_value = [5]
        with app.app_context():
            kw = TrackedKeyword(keyword='AI')
            db.session.add(kw)
            db.session.commit()
            keyword_id = kw.id
        response = self.app.get(f'/api/seo-dashboard/keyword/{keyword_id}')
        self.assertEqual(response.status_code, 200)

class SchedulerApiTestCase(BaseTestCase):
    def test_create_post(self):
        response = self.app.post('/api/posts',
                                 data=json.dumps({'title': 'Test Post', 'topic': 'testing'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        with app.app_context():
            self.assertEqual(BlogPost.query.count(), 1)
            self.assertEqual(BlogPost.query.first().title, 'Test Post')

    @patch('app.recommendation_service.recommend_publishing_time')
    @patch('app.get_historical_interest')
    def test_get_recommendations(self, mock_get_historical, mock_recommend):
        mock_get_historical.return_value = [{'date': '2023-01-01T10:00:00', 'testing': 100}]
        mock_recommend.return_value = {'day': 'Monday', 'hour': 10}

        response = self.app.get('/api/recommendations?topic=testing')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['day'], 'Monday')
        mock_get_historical.assert_called_once_with(keywords=['testing'], years=1)

    @patch('app.wordpress_service.schedule_post_on_wordpress')
    def test_update_post_to_schedule(self, mock_schedule_post):
        mock_schedule_post.return_value = {'status': 'success'}
        with app.app_context():
            # Create a mock integration and a post
            integration = PlatformIntegration(platform_name='wordpress', site_url='test.com', api_key='fake_key')
            post = BlogPost(title='Scheduling Test', topic='schedule', platform=integration)
            db.session.add(integration)
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        scheduled_time = datetime.utcnow().isoformat()
        response = self.app.put(f'/api/posts/{post_id}',
                                data=json.dumps({'status': 'scheduled', 'scheduled_time': scheduled_time}),
                                content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_schedule_post.assert_called_once()
        with app.app_context():
            updated_post = BlogPost.query.get(post_id)
            self.assertEqual(updated_post.status, 'scheduled')


if __name__ == '__main__':
    unittest.main()
