from models import db, Product, PricingRule
from trends_service import get_interest_over_time
import shopify_service

def calculate_dynamic_price(product_id):
    """
    Calculates a dynamic price for a product based on its pricing rule and current Google Trends data.
    """
    product = Product.query.get(product_id)
    if not product or not product.pricing_rule:
        return None

    rule = product.pricing_rule

    # Fetch current price from Shopify (mocked)
    # In a real app, you might need to get the variant ID first
    variants = shopify_service.get_product_variants(None, None, product.id)
    if not variants or not variants.get('variants'):
        return None
    current_price = variants['variants'][0].get('price', 100) # Default price for mock

    # Fetch latest Google Trends data
    trends_data = get_interest_over_time([product.name])
    if not trends_data:
        return None

    latest_trend_value = trends_data[-1][product.name]

    new_price = float(current_price)

    if latest_trend_value > rule.trend_threshold:
        adjustment_factor = 1 + (rule.price_adjustment_percentage / 100.0)
        new_price *= adjustment_factor

    # Apply floor and ceiling
    if rule.price_floor is not None:
        new_price = max(new_price, rule.price_floor)
    if rule.price_ceiling is not None:
        new_price = min(new_price, rule.price_ceiling)

    return {
        'product_id': product.id,
        'original_price': float(current_price),
        'dynamic_price': round(new_price, 2),
        'trend_value': latest_trend_value,
        'trend_threshold': rule.trend_threshold
    }
