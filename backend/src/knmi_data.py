import knmi
import sqlite3
from datetime import datetime, timedelta

def get_all_hourly_outside_temp_from_yesterday():
    today = datetime.today()
    presentday = today.strftime('%Y%m%d')
    yesterday = (today - timedelta(1)).strftime('%Y%m%d')
    df = knmi.get_hour_data_dataframe(stations=[260], start=yesterday, end=today).reset_index()
    df = df[['YYYYMMDD_H', 'STN', 'T']]
    df['T'] = df['T'] * 0.1
    return df

def initiate_table():
    curs.execute(
        """CREATE TABLE KNMI_data ( timestamp_h DATETIME,
                                    station NUMERIC,
                                    temp NUMERIC)"""
    )

def add_day_dataframe(df):
    for row, value in df.iterrows():
        time = value['YYYYMMDD_H'].strftime("%B %d, %Y %I:%M%p")  # format for sql
        station = value['STN']
        temp = round(value['T'], 2)
        curs.execute(
            "INSERT INTO KNMI_data values((?), (?), (?))",  # noqa: E501
            (time, station, temp),
        )
        conn.commit()
    conn.close()    

if __name__ == "__main__":
    # create database table
    conn = sqlite3.connect("knmiData.db")
    curs = conn.cursor()

    # get and impute data in database and table
    df = get_all_hourly_outside_temp_from_yesterday()  
    try:
        add_day_dataframe(df)
    except sqlite3.OperationalError:
        initiate_table()
        add_day_dataframe(df)        