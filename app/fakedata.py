from random import randint
import datetime
import pytz
import pandas as pd
import numpy as np

np.random.seed(345354)

def get_data(start, end, f='5T'):
    """Generate fake data between start and dates"""
    date_list = pd.to_datetime(pd.date_range(start, end, freq=f))

    data = pd.DataFrame({
        'Date': date_list,
        'Interval': pd.Series(date_list).dt.strftime('%H%M').astype('int64'),
        'Cars': [(5 + np.random.randint(-5, 10)) for x in date_list],
        'Trucks': [(5 + np.random.randint(-5, 10)) for x in date_list]
        }
    )

    data['Total'] = data['Cars'] + data['Trucks']

    return data


if __name__ == "__main__":
    # Generate fake data for 31 days at 5 minute intervals (288 five minute intervals per day)
    fake_data = get_data('2019-01-01T00:00:00Z', '2019-04-01T00:00:00Z')

    # Get the average over each Interval
    fdbyint = fake_data.groupby('Interval').agg({'Total': np.average})