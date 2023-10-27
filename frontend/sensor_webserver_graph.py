from flask import Flask
from flask import render_template
from flask import make_response
import sqlite3
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import datetime as dt


def sql_extract_sensor_dataframe():
    conn = sqlite3.connect("../sensor-temperature-air-cron-job/sensorsData.db")
    df = pd.read_sql_query("SELECT * FROM DHT_data", conn)
    # df_100 = df.tail(50)
    last_row = df.iloc[-1:]
    return df, last_row


app = Flask(__name__)


@app.route("/")
def homepage():
    df, last_row = sql_extract_sensor_dataframe()
    timestamp = last_row["timestamp"].values[0]
    pi_temperature = last_row["temp_pi"].values[0]
    house_humidity = last_row["hum_house"].values[0]
    house_temperature = last_row["temp_house"].values[0]
    templateData = {
        "title": "Sensor information",
        "temp_pi": pi_temperature,
        "temp_home": house_temperature,
        "lucht_home": house_humidity,
        "timestamp": timestamp,
    }
    return render_template("index.html", **templateData)


@app.route("/temp")
def plot_temp():
    df, last_row = sql_extract_sensor_dataframe()
    df["time"] = pd.to_datetime(df["timestamp"])
    today = pd.Timestamp.today().day
    month = pd.Timestamp.today().month
    tomorrow = today + 1
    y = df["temp_house"]
    x = df["time"]
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperature [°C]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    axis.set_ylim([10, 30])
    axis.set_xlim([dt.date(2022, month, 1), dt.date(2022, month, tomorrow)])
    axis.plot(x, y)
    axis.tick_params(axis="x", rotation=30)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


@app.route("/hum")
def plot_hum():
    df, last_row = sql_extract_sensor_dataframe()
    df["time"] = pd.to_datetime(df["timestamp"])
    today = pd.Timestamp.today().day
    month = pd.Timestamp.today().month
    tomorrow = today + 1
    x = df["time"]
    y = df["hum_house"]
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Humidity [%]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    axis.set_ylim([20, 80])
    axis.set_xlim([dt.date(2022, month, 1), dt.date(2022, month, tomorrow)])
    axis.plot(x, y)
    axis.tick_params(axis="x", rotation=30)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="huiskamer")
