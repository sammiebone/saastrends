from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TrackedKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False, unique=True)
    ranks = db.relationship('KeywordRank', backref='keyword', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword
        }

    def __repr__(self):
        return f'<TrackedKeyword {self.keyword}>'

class KeywordRank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    tracked_keyword_id = db.Column(db.Integer, db.ForeignKey('tracked_keyword.id'), nullable=False)

    def __repr__(self):
        return f'<KeywordRank {self.keyword.keyword} - {self.date} - Rank: {self.rank}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft') # e.g., draft, scheduled, published
    scheduled_time = db.Column(db.DateTime, nullable=True)
    platform_integration_id = db.Column(db.Integer, db.ForeignKey('platform_integration.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'topic': self.topic,
            'content': self.content,
            'status': self.status,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'platform_integration_id': self.platform_integration_id
        }

    def __repr__(self):
        return f'<BlogPost {self.title}>'

class PlatformIntegration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(50), nullable=False) # 'wordpress', 'medium', etc.
    site_url = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False) # For Application Passwords in WordPress
    posts = db.relationship('BlogPost', backref='platform', lazy=True)

    def __repr__(self):
        return f'<PlatformIntegration {self.platform_name} - {self.site_url}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }

    def __repr__(self):
        return f'<Product {self.name}>'

class PricingRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, unique=True)
    trend_threshold = db.Column(db.Float, nullable=False)
    price_adjustment_percentage = db.Column(db.Float, nullable=False)
    price_floor = db.Column(db.Float, nullable=True)
    price_ceiling = db.Column(db.Float, nullable=True)

    product = db.relationship('Product', backref=db.backref('pricing_rule', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'trend_threshold': self.trend_threshold,
            'price_adjustment_percentage': self.price_adjustment_percentage,
            'price_floor': self.price_floor,
            'price_ceiling': self.price_ceiling
        }
