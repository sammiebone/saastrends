from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta

def get_trending_searches(pn='united_states'):
    """
    Fetches the latest trending searches for a given country.
    :param pn: The country name, e.g., 'united_states', 'japan'.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        trending_df = pytrends.trending_searches(pn=pn)
        if isinstance(trending_df, pd.DataFrame) and not trending_df.empty:
            # The result is a DataFrame with a single column of trend names
            return trending_df[0].tolist()
    except Exception as e:
        print(f"An error occurred while fetching trending searches: {e}")
    return []

def get_rising_queries(keyword, timeframe='today 3-m', geo='', cat=0, gprop=''):
    """
    Fetches rising search queries related to a given keyword, with filters.
    """
    pytrends = TrendReq(hl='en-US', tz=360)

    try:
        pytrends.build_payload(
            kw_list=[keyword],
            cat=cat,
            timeframe=timeframe,
            geo=geo,
            gprop=gprop
        )
        related_queries = pytrends.related_queries()

        if keyword in related_queries and 'rising' in related_queries[keyword]:
            rising_df = related_queries[keyword]['rising']
            if isinstance(rising_df, pd.DataFrame) and not rising_df.empty:
                return rising_df.to_dict('records')
    except Exception as e:
        print(f"An error occurred while fetching rising queries: {e}")

    return []

def get_interest_over_time(keywords, timeframe='today 12-m', geo='', cat=0, gprop=''):
    """
    Fetches interest over time for a list of keywords.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        pytrends.build_payload(
            kw_list=keywords,
            cat=cat,
            timeframe=timeframe,
            geo=geo,
            gprop=gprop
        )
        interest_df = pytrends.interest_over_time()
        if isinstance(interest_df, pd.DataFrame) and not interest_df.empty:
            # Reset index to make 'date' a column
            interest_df = interest_df.reset_index()
            # Convert date to string to be JSON serializable
            interest_df['date'] = interest_df['date'].astype(str)
            # Drop the 'isPartial' column if it exists
            if 'isPartial' in interest_df.columns:
                interest_df = interest_df.drop(columns=['isPartial'])
            return interest_df.to_dict('records')
    except Exception as e:
        print(f"An error occurred while fetching interest over time: {e}")
    return []

def get_historical_interest(keywords, years=1):
    """
    Fetches historical hourly interest for a list of keywords for the past N years.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        # Set the end date to today and start date to N years ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        # pytrends.get_historical_interest can be flaky for long date ranges,
        # but we'll try it for the specified period.
        hist_df = pytrends.get_historical_interest(
            keywords=keywords,
            year_start=start_date.year,
            month_start=start_date.month,
            day_start=start_date.day,
            year_end=end_date.year,
            month_end=end_date.month,
            day_end=end_date.day,
            sleep=1 # Be respectful of Google's rate limits
        )

        if isinstance(hist_df, pd.DataFrame) and not hist_df.empty:
            hist_df = hist_df.reset_index()
            hist_df['date'] = hist_df['date'].astype(str)
            if 'isPartial' in hist_df.columns:
                hist_df = hist_df.drop(columns=['isPartial'])
            return hist_df.to_dict('records')

    except Exception as e:
        print(f"An error occurred while fetching historical interest: {e}")
    return []
