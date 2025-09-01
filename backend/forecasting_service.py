import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def generate_forecast(historical_data, keyword, steps=12):
    """
    Generates a future trend forecast using an ARIMA model.

    :param historical_data: A list of dictionaries from the trends_service.
    :param keyword: The keyword column to use for forecasting.
    :param steps: The number of future steps to forecast (e.g., 12 weeks for 3 months).
    :return: A list of forecasted values, or None if forecasting fails.
    """
    if not historical_data:
        return None

    df = pd.DataFrame(historical_data)

    if keyword not in df.columns or df[keyword].isnull().all():
        return None

    # Ensure the date column is datetime and set it as the index
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    # Use the keyword's interest value as the time series data
    time_series = df[keyword]

    # Resample to weekly frequency to handle any gaps and ensure regularity, forward-fill missing values
    time_series = time_series.asfreq('W-MON').ffill()

    if time_series.empty:
        return None

    try:
        # A simple ARIMA model. These parameters (p,d,q) are common starting points.
        # p: The number of lag observations included in the model (lag order).
        # d: The number of times that the raw observations are differenced (degree of differencing).
        # q: The size of the moving average window (order of moving average).
        model = ARIMA(time_series, order=(5, 1, 0))
        model_fit = model.fit()

        # Generate forecast for the next N steps
        forecast = model_fit.forecast(steps=steps)

        if forecast is not None:
            # Create a date range for the forecast
            last_date = time_series.index[-1]
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=steps, freq='W-MON')

            # Combine dates and forecast values
            forecast_result = [{'date': date.strftime('%Y-%m-%d'), 'forecast_value': value} for date, value in zip(forecast_dates, forecast)]
            return forecast_result

    except Exception as e:
        print(f"An error occurred during forecasting: {e}")

    return None
