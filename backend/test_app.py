import unittest
from unittest.mock import patch
import json
from datetime import datetime
from app import app, db, TrackedKeyword, BlogPost, PlatformIntegration, Product
import recommendation_service
import forecasting_service

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

# ... (Previous test classes are assumed to be here and correct) ...
class TrendsApiTestCase(BaseTestCase):
    @patch('app.get_rising_queries')
    def test_content_ideas_success(self, mock_get_rising_queries):
        mock_get_rising_queries.return_value = [{'query': 'ai in marketing', 'value': 150}]
        response = self.app.get('/api/content-ideas?topic=AI')
        self.assertEqual(response.status_code, 200)
    @patch('app.get_trending_searches')
    def test_trending_topics_success(self, mock_get_trending_searches):
        mock_get_trending_searches.return_value = ['SaaS', 'AI', 'Fintech']
        response = self.app.get('/api/trending-topics?pn=japan')
        self.assertEqual(response.status_code, 200)

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

class SchedulerApiTestCase(BaseTestCase):
    def test_create_post(self):
        response = self.app.post('/api/posts', data=json.dumps({'title': 'Test Post', 'topic': 'testing'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
    @patch('app.recommendation_service.recommend_publishing_time')
    @patch('app.get_historical_interest')
    def test_get_recommendations(self, mock_get_historical, mock_recommend):
        mock_get_historical.return_value = [{'date': '2023-01-01T10:00:00', 'testing': 100}]
        mock_recommend.return_value = {'day': 'Monday', 'hour': 10}
        response = self.app.get('/api/recommendations?topic=testing')
        self.assertEqual(response.status_code, 200)

class ForecasterApiTestCase(BaseTestCase):
    def test_add_product(self):
        response = self.app.post('/api/products',
                                 data=json.dumps({'name': 'Cool T-Shirt', 'category': 'Apparel'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        with app.app_context():
            self.assertEqual(Product.query.count(), 1)
            self.assertEqual(Product.query.first().name, 'Cool T-Shirt')

    @patch('app.forecasting_service.generate_forecast')
    @patch('app.get_interest_over_time')
    def test_get_product_forecast(self, mock_get_interest, mock_forecast):
        mock_get_interest.return_value = [{'date': '2023-01-01', 'T-Shirt': 75}]
        mock_forecast.return_value = [{'date': '2023-01-08', 'forecast_value': 80}]
        with app.app_context():
            prod = Product(name='T-Shirt')
            db.session.add(prod)
            db.session.commit()
            product_id = prod.id

        response = self.app.get(f'/api/products/{product_id}/forecast')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('historical', data)
        self.assertIn('forecast', data)
        self.assertEqual(data['forecast'][0]['forecast_value'], 80)

    @patch('app.shopify_service.get_shopify_products')
    def test_import_from_shopify(self, mock_get_products):
        mock_get_products.return_value = {
            'products': [
                {'id': 101, 'title': 'The Coolest T-Shirt', 'product_type': 'Apparel'},
                {'id': 102, 'title': 'The Best Mug', 'product_type': 'Kitchenware'},
            ]
        }
        response = self.app.post('/api/products/import-from-shopify')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['imported'], 2)
        with app.app_context():
            self.assertEqual(Product.query.count(), 2)

if __name__ == '__main__':
    unittest.main()
