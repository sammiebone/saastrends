import pandas as pd

def recommend_publishing_time(historical_data, keyword):
    """
    Analyzes historical trend data to recommend the best time to publish.

    :param historical_data: A list of dictionaries, where each dict has a 'date' and a keyword value.
    :param keyword: The keyword to analyze from the historical data.
    :return: A dictionary with the recommended day of the week and hour, or None if no recommendation can be made.
    """
    if not historical_data:
        return None

    df = pd.DataFrame(historical_data)

    if keyword not in df.columns:
        return None

    # Convert date column to datetime objects
    df['date'] = pd.to_datetime(df['date'])

    # Extract day of week and hour
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour

    # Group by day and hour and calculate the mean interest
    avg_interest = df.groupby(['day_of_week', 'hour'])[keyword].mean().reset_index()

    if avg_interest.empty:
        return None

    # Find the row with the maximum average interest
    best_time = avg_interest.loc[avg_interest[keyword].idxmax()]

    return {
        'day': best_time['day_of_week'],
        'hour': int(best_time['hour']),
        'avg_interest': best_time[keyword]
    }
