from flask import Flask
from flask import render_template
from flask import make_response
import sqlite3
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import io
import datetime as dt


def sql_extract_sensor_dataframe():
    conn = sqlite3.connect("../backend/sensorData.db")
    df = pd.read_sql_query("SELECT * FROM DHT_data", conn)
    last_row = df.iloc[-1:]
    return df, last_row

def sql_extract_knmi_dataframe():
    conn = sqlite3.connect("../backend/knmiData.db")
    dfknmi = pd.read_sql_query("SELECT * FROM KNMI_data", conn)
    return dfknmi    

def create_results_dataframe(df, dfknmi):
    df['key'] = pd.to_datetime(df['timestamp']).dt.strftime("%d%H")
    dfknmi['key'] = pd.to_datetime(dfknmi['timestamp_h']).dt.strftime("%d%H")
    result = df.merge(dfknmi, left_on='key', right_on='key', how='left')
    return result

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
    dfknmi = sql_extract_knmi_dataframe()
    result = create_results_dataframe(df, dfknmi)
    result["time"] = pd.to_datetime(result["timestamp"])
    today = pd.Timestamp.today().day
    month = pd.Timestamp.today().month
    tomorrow = today + 1
    y1 = result["temp_house"]
    y2 = result["hum_house"]
    y3 = result['temp']
    x = result["time"]
    fig = Figure(figsize=(10, 8))
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperatuur [°C] and Luchtvochtigheid (R%)")
    axis.set_xlabel("Datum en tijd van de meeting")
    axis.set_ylabel("Temperatuur en luchtvochtigheid")
    axis.grid(True)
    axis.set_ylim([0, 80])
    axis.set_xlim([dt.date(2023, month, today - 3), dt.date(2023, month, today + 3)])
    axis.plot(x, y1, color='blue')
    axis.plot(x, y2, color='orange')
    axis.plot(x, y3, color='grey')
    axis.tick_params(axis="x", rotation=30, labelsize=16)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


@app.route("/hum")
def plot_hum():
    df, last_row = sql_extract_sensor_dataframe()
    dfknmi = sql_extract_knmi_dataframe()
    result = create_results_dataframe(df, dfknmi)    
    result["time"] = pd.to_datetime(result["timestamp"])
    today = pd.Timestamp.today().day
    month = pd.Timestamp.today().month
    tomorrow = today + 1
    x = result["time"]
    y1 = result["temp_house"]
    fig = Figure(figsize=(10, 8))
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperatuur [°C]")
    axis.set_xlabel("Tijdstip van de meeting")
    axis.set_ylabel("Temperatuur")
    axis.grid(True)
    xformatter = mdates.DateFormatter('%H:%M')
    axis.xaxis.set_major_formatter(xformatter)    
    axis.axhline(19, color='red')
    axis.set_ylim([15, 25])
    axis.set_xlim([dt.date(2023, month, today), dt.date(2023, month, tomorrow)])
    axis.plot(x, y1, color='blue')
    axis.tick_params(axis="x", rotation=30, labelsize=16)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()   
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="huiskamer")
