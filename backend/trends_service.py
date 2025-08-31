from pytrends.request import TrendReq
import pandas as pd

def get_rising_queries(keyword):
    """
    Fetches rising search queries related to a given keyword.
    """
    pytrends = TrendReq(hl='en-US', tz=360)

    try:
        pytrends.build_payload(kw_list=[keyword], cat=0, timeframe='today 3-m', geo='', gprop='')
        related_queries = pytrends.related_queries()

        if keyword in related_queries and 'rising' in related_queries[keyword]:
            rising_df = related_queries[keyword]['rising']
            if isinstance(rising_df, pd.DataFrame) and not rising_df.empty:
                return rising_df.to_dict('records')
    except Exception as e:
        print(f"An error occurred: {e}")

    return []
