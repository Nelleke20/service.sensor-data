from gpiozero import CPUTemperature
import sqlite3
from datetime import datetime
import board
import adafruit_dht


def get_sensor_data():
    dhtDevice = adafruit_dht.DHT22(board.D4)
    pi_temperature = round(CPUTemperature().temperature, 2)
    house_temperature = round(dhtDevice.temperature, 2)
    house_humidity = round(dhtDevice.humidity, 2)   
    return pi_temperature, house_humidity, house_temperature


def get_sensor_data_dummy():
    pi_temperature = 30
    house_humidity = 76
    house_temperature = 24
    return pi_temperature, house_humidity, house_temperature


def initiate_table():
    curs.execute(
        """CREATE TABLE DHT_data (  timestamp DATETIME,
                                    temp_pi NUMERIC,
                                    temp_house NUMERIC,
                                    hum_house NUMERIC)"""
    )


def recreate_table():
    curs.execute("DROP TABLE IF EXISTS DHT_data")
    curs.execute(
        """CREATE TABLE DHT_data (  timestamp DATETIME,
                                    temp_pi NUMERIC,
                                    temp_house NUMERIC,
                                    hum_house NUMERIC)"""
    )


def add_data(temp_pi, temp_house, hum_house):
    curs.execute(
        "INSERT INTO DHT_data values(datetime('now'), (?), (?), (?))",  # noqa: E501
        (temp_pi, temp_house, hum_house),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # create database table
    conn = sqlite3.connect("sensorData.db")
    curs = conn.cursor()
    today = int(datetime.today().strftime("%d"))
    if today == 1:  # only create table every first of the month
        recreate_table()

    # impute data
    (
        pi_temperature,
        house_humidity,
        house_temperature,
    ) = get_sensor_data()  # test with dummy by using function with dummy 
    try:
        add_data(pi_temperature, house_temperature, house_humidity)
    except sqlite3.OperationalError:
        initiate_table()
        add_data(pi_temperature, house_temperature, house_humidity)