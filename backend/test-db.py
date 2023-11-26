import pandas as pd
import sqlite3

# connect with the database which is relevant
db_path = "sensorData.db"
conn = sqlite3.connect(db_path)

# check what is in the database table by create a DataFrame
df = pd.read_sql_query("SELECT * FROM DHT_data", conn)

# show datafame and see what is in it
print(df.head())
print("\n")
print(pd.Timestamp.today().day)
