import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import json
from requests.auth import HTTPBasicAuth
import os
import pyodbc
try:
    now = datetime.now()
    formatDateTime = now.strftime("%d/%m/%Y %H:%M")
    db_date = now.strftime("%Y-%m-%d")
    db_time = now.strftime("%H:%M")
except Exception as e:
    formatDateTime = None
    with open ('logfile.log', 'a') as file:
        file.write(f"""Problem with date: {str(e)}\n""")

#load env variables
try:
    load_dotenv()
    username = os.getenv('bc_username')
    user_password = os.getenv('bc_password')
    url = os.getenv('bc_url')
    mdms_url = os.getenv('bc_mdms_url')
    server = os.getenv('db_server')
    database = os.getenv('db_db')
    db_username = os.getenv('db_user')
    db_password = os.getenv('db_password')
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with importing env variables: {str(e)}\n""")


try:
    response = requests.get(url, auth=HTTPBasicAuth(username, user_password))
    final_d = {}
    print(response.status_code)
    # Check if the request was successful
    if response.status_code == 200:
        # Process the data
        data = response.json()
        for row in data['value']:
            key = row['ID']
            final_d[key] = {
            'Status': row['Status'],
            'Object_ID_to_Run': row['Object_ID_to_Run'],
            'Object_Caption_to_Run': row['Object_Caption_to_Run'],
            'Description': row['Description'],
            'Error_Message': row['Error_Message'],
            'ID': row['ID'],
            'User_ID': row['User_ID'],
            'Object_Type_to_Run': row['Object_Type_to_Run'],
            'Object_ID_to_Run': row['Object_ID_to_Run'],
            'Object_Caption_to_Run': row['Object_Caption_to_Run'], 
            'Description': row['Description'], 
            'Error_Message': row['Error_Message']  
        }
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with reading API data: {str(e)}\n""")               
print(final_d)
try:    #MDMS
    response = requests.get(mdms_url, auth=HTTPBasicAuth(username, user_password))
    if response.status_code == 200:
        # Process the data
        data = response.json()
        for row in data['value']:
            key = row['ID']
            final_d[key] = {
            'Status': row['Status'],
            'Object_ID_to_Run': row['Object_ID_to_Run'],
            'Object_Caption_to_Run': row['Object_Caption_to_Run'],
            'Description': row['Description'],
            'Error_Message': row['Error_Message'],
            'ID': row['ID'],
            'User_ID': row['User_ID'],
            'Object_Type_to_Run': row['Object_Type_to_Run'],
            'Object_ID_to_Run': row['Object_ID_to_Run'],
            'Object_Caption_to_Run': row['Object_Caption_to_Run'], 
            'Description': row['Description'], 
            'Error_Message': row['Error_Message']  
        }  
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with reading Mdms API data: {str(e)}\n""")

try:
    ignore_queues = [] #by Object_ID_to_Run INT
    db_queues = {}
    for k,v in final_d.items():
        if v['Status'] == 'Error' and v['Object_ID_to_Run'] not in ignore_queues:
            task_name = f"{v['Object_Caption_to_Run']} - {v['Description']}"
            db_queues[v['ID']] = {
                "task_name": task_name,
                "User_ID": v['User_ID'],
                "Object_Type_to_Run": v['Object_Type_to_Run'],
                "Object_ID_to_Run": v['Object_ID_to_Run'],
                "Object_Caption_to_Run": v['Object_Caption_to_Run'],
                "Description": v['Description'],
                "Error_Message": v['Error_Message']
            }
            
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with creating error queues dict: {str(e)}\n""")          
# insert to db statistics
try:
    server = os.getenv('db_server')
    database = os.getenv('db_db')
    username = os.getenv('db_user')
    password = os.getenv('db_password')

    # Connect to SQL Server
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={db_username};PWD={db_password}"
    )
    cursor = conn.cursor()
    for id, data in db_queues.items():
        task_name = data["task_name"]
        user_id = data["User_ID"]
        object_type_to_run = data["Object_Type_to_Run"]
        object_id_to_run = data["Object_ID_to_Run"]
        object_caption_to_run = data["Object_Caption_to_Run"]
        description = data["Description"]
        error_message = data["Error_Message"]

        cursor.execute(
            """
            INSERT INTO workhours_queues (
                task_name, date, time, queue_id, User_ID, Object_Type_to_Run,
                Object_ID_to_Run, Object_Caption_to_Run, Description, Error_Message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (task_name, db_date, db_time, id, user_id, object_type_to_run,
            object_id_to_run, object_caption_to_run, description, error_message)
        )

# Commit the transaction
    conn.commit()
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem with database import: {str(e)}\n""")