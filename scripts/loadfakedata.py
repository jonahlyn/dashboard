#!/usr/bin/env python3

#
# Loads fake data into the database
#

from random import randint
import datetime
import pytz
import pandas as pd
import numpy as np
import mysql.connector
from sqlalchemy import create_engine

# Load configuration
from config import DATABASE_URI

np.random.seed(345354)


def get_data(start, end, f='5T'):
    """Generate fake data between start and dates"""
    date_list = pd.to_datetime(pd.date_range(start, end, freq=f))

    data = pd.DataFrame({
        'date': date_list,
        'vehicles': [(5 + np.random.randint(-5, 10)) for x in date_list],
        'filename': "output_20190402201820.png"
        }
    )

    return data


if __name__ == "__main__":
    # Generate fake data for 31 days at 5 minute intervals (288 five minute intervals per day)
    fake_data = get_data('2019-01-01T00:00:00Z', '2019-04-01T00:00:00Z')

    # Create a database connection and write the dataframe to data table
    engine = create_engine(DATABASE_URI, echo=False)
    fake_data.to_sql(name = 'data', 
        con = engine, 
        if_exists = 'replace', 
        index = True, 
        index_label = 'id')
