from gpiozero import CPUTemperature
import sqlite3
from datetime import datetime

# import Adafruit_DHT as ada


def get_sensor_data():
    pi_temperature = round(CPUTemperature().temperature, 2)
    house_hum, house_temperature = ada.read_retry(ada.DHT22, 4)  # noqa:F821
    house_humidity = round(house_hum, 2)
    house_temperature = round(house_temperature, 2)
    return pi_temperature, house_humidity, house_temperature


def get_sensor_data_dummy():
    pi_temperature = 80
    house_humidity = 30
    house_temperature = 20
    return pi_temperature, house_humidity, house_temperature


def initiate_table():
    curs.execute(
        """CREATE TABLE DHT_data (  timestamp DATETIME,
                                    temp_pi NUMERIC,
                                    temp_house NUMERIC,
                                    hum_house NUMERIC)"""
    )  # noqa: E501


def recreate_table():
    curs.execute("DROP TABLE IF EXISTS DHT_data")
    curs.execute(
        """CREATE TABLE DHT_data (  timestamp DATETIME,
                                    temp_pi NUMERIC,
                                    temp_house NUMERIC,
                                    hum_house NUMERIC)"""
    )  # noqa: E501


def add_data(temp_pi, temp_house, hum_house):
    curs.execute(
        "INSERT INTO DHT_data values(datetime('now'), (?), (?), (?))",
        (temp_pi, temp_house, hum_house),
    )  # noqa: E501
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # create database table
    conn = sqlite3.connect("sensorsData.db")
    curs = conn.cursor()
    today = int(datetime.today().strftime("%d"))
    if today == 1:  # only create table every first of the month
        recreate_table()

    # impute data
    (
        pi_temperature,
        house_humidity,
        house_temperature,
    ) = get_sensor_data_dummy()  # test with dummy
    try:
        add_data(pi_temperature, house_temperature, house_humidity)
    except sqlite3.OperationalError:
        initiate_table()
