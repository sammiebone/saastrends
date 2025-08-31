from pytrends.request import TrendReq
import pandas as pd

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
