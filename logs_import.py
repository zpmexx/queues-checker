import pyodbc
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()
#mail
from_address = os.getenv('from_address')
to_address_str = os.getenv('to_address')
password = os.getenv('password')

server = os.getenv('db_server')
database = os.getenv('db_db')
username = os.getenv('db_user')
password = os.getenv('db_password')

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()


file_path = 'logimport.txt' 
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

tasks = []
current_date = None

for line in lines:
    line = line.strip()
    if '/' in line and ':' in line: 
        date, time = line.split(' ')
        formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
        current_date = formatted_date
        current_time = time
    elif current_date:  
        tasks.append((line, current_date, current_time))

for task_name, date, time in tasks:
    cursor.execute(
        "INSERT INTO disconnected_queues (task_name, date, time) VALUES (?, ?, ?)",
        (task_name, date, time)
    )
conn.commit()

cursor.close()
conn.close()