import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def generate_forecast(historical_data, sales_data, keyword, steps=12):
    """
    Generates a future trend forecast using an ARIMAX model, incorporating sales data.

    :param historical_data: A list of dictionaries from the trends_service.
    :param sales_data: A list of sales data dictionaries from shopify_service.
    :param keyword: The keyword column to use for forecasting.
    :param steps: The number of future steps to forecast.
    :return: A list of forecasted values, or None if forecasting fails.
    """
    if not historical_data:
        return None

    # Process Google Trends data
    trends_df = pd.DataFrame(historical_data)
    if keyword not in trends_df.columns or trends_df[keyword].isnull().all():
        return None
    trends_df['date'] = pd.to_datetime(trends_df['date'])
    trends_df = trends_df.set_index('date')
    time_series = trends_df[keyword].asfreq('W-MON').ffill()

    # Process sales data
    sales_df = pd.DataFrame(sales_data)
    sales_df['date'] = pd.to_datetime(sales_df['created_at'])
    sales_df = sales_df.set_index('date')
    # Extract quantity from the nested line_items structure
    sales_df['quantity'] = sales_df['line_items'].apply(lambda items: items[0]['quantity'] if items else 0)
    sales_time_series = sales_df['quantity'].resample('W-MON').sum()

    # Align the two time series
    combined_df = pd.concat([time_series, sales_time_series], axis=1).ffill().fillna(0)

    endog = combined_df[keyword]
    exog = combined_df[['quantity']]

    if endog.empty:
        return None

    try:
        # ARIMAX model, with sales data as an exogenous variable.
        model = ARIMA(endog, exog=exog, order=(5, 1, 0))
        model_fit = model.fit()

        # For forecasting, we need future values of the exogenous variable.
        # As a simple approach, we'll assume future sales follow the last known value.
        last_sales_value = exog.iloc[-1]
        future_exog = pd.DataFrame({'quantity': [last_sales_value['quantity']] * steps},
                                   index=pd.date_range(start=endog.index[-1] + pd.Timedelta(weeks=1), periods=steps, freq='W-MON'))

        forecast = model_fit.forecast(steps=steps, exog=future_exog)

        if forecast is not None:
            # Create a date range for the forecast
            last_date = endog.index[-1]
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(weeks=1), periods=steps, freq='W-MON')

            # Combine dates and forecast values
            forecast_result = [{'date': date.strftime('%Y-%m-%d'), 'forecast_value': value} for date, value in zip(forecast_dates, forecast)]
            return forecast_result

    except Exception as e:
        print(f"An error occurred during forecasting: {e}")

    return None
