import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import json
from requests.auth import HTTPBasicAuth
import os

load_dotenv()
#mail
from_address = os.getenv('from_address')
to_address_str = os.getenv('to_address')
password = os.getenv('password')

#api endpoint
username = os.getenv('bc_username')
user_password = os.getenv('bc_password')
url = os.getenv('bc_url')
mdms_url = os.getenv('bc_mdms_url')

now = datetime.now()
formatDateTime = now.strftime("%d/%m/%Y %H:%M")


response = requests.get(url, auth=HTTPBasicAuth(username, user_password))
final_d = {}
# Check if the request was successful
if response.status_code == 200:
    # Process the data
    data = response.json()
    for row in data['value']:
        key = row['ID']
        final_d[key] = {'Status': row['Status'],
                        'Object_ID_to_Run': row['Object_ID_to_Run'],
                        'Object_Caption_to_Run': row['Object_Caption_to_Run'],
                        'Description': row['Description'],
                        'Error_Message': row['Error_Message'],
                         }        
else:
    with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem z uzyskaniem odpowiedzi""")
            
            
#MDMS
response = requests.get(mdms_url, auth=HTTPBasicAuth(username, user_password))
if response.status_code == 200:
    # Process the data
    data = response.json()
    for row in data['value']:
        key = row['ID']
        final_d[key] = {'Status': row['Status'],
                        'Object_ID_to_Run': row['Object_ID_to_Run'],
                        'Object_Caption_to_Run': row['Object_Caption_to_Run'],
                        'Description': row['Description'],
                        'Error_Message': row['Error_Message'],
                         }        
else:
    with open ('logfile.log', 'a') as file:
            file.write(f"""{formatDateTime} Problem z uzyskaniem odpowiedzi""")
#for k,v in final_d.items():
#    print(k, v)
body = "" 

ignore_queues = [] #by Object_ID_to_Run INT
queues_with_error = []
for k,v in final_d.items():
    if v['Status'] == 'Error' and v['Object_ID_to_Run'] not in ignore_queues:
        queues_with_error.append(f"""{v['Object_Caption_to_Run']} - {v['Description']}""")
        body += f"""<h1 style="color:red">Kolejka: {v['Object_Caption_to_Run']} - {v['Description']}</h1>\n
        <h2>Bład: {v['Error_Message']}</h2>\n"""
#print(body)   

bc_currency = os.getenv('bc_currency')
mdms_currency = os.getenv('mdms_currency')
nbpEurUrl = os.getenv('nbpEurUrl')

#nbp
response = requests.get(nbpEurUrl, auth=HTTPBasicAuth(username, user_password))
if response.status_code == 200:
    data = response.json()
    # print(data)
    nbpEur = data['rates'][0]['mid']
else:
    body += f"Problem z odpytaniem strony NBP.\n"
 
#cdrl
response = requests.get(bc_currency, auth=HTTPBasicAuth(username, user_password))
if response.status_code == 200:
    data = response.json()
    for line in data['value']:
        if line['Code'] == 'EUR':
            if line['ExchangeRateAmt'] != nbpEur:
                body += f"Błedna waluta na CDRL.\n Poprawna -> {nbpEur} obecna -> {line['ExchangeRateAmt']}"
            break
else:
    body += f"Problem z wczytaniem waluty na CDRL"
    
#mdms_currency
response = requests.get(mdms_currency, auth=HTTPBasicAuth(username, user_password))
if response.status_code == 200:
    data = response.json()
    for line in data['value']:
        if line['Code'] == 'EUR':
            if line['ExchangeRateAmt'] != nbpEur:
                body += f"Błedna waluta na MDMS.\n Poprawna -> {nbpEur} obecna -> {line['ExchangeRateAmt']}"
            break
else:
    body += f"Problem z wczytaniem waluty na MDMS"


to_address = json.loads(to_address_str)
msg = MIMEMultipart()
msg['From'] = from_address
msg["To"] = ", ".join(to_address)
msg['Subject'] = f"Sprzawdzenie kolejek data: {formatDateTime}."
#print(", ".join(to_address))
#body = ""
if body:
    msg.attach(MIMEText(body, 'html'))
else:
    msg.attach(MIMEText("Brak błędów. Waluty ok.", 'html'))
try:
    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()               
except Exception as e:
    with open ('logfile.log', 'a') as file:
        file.write(f"""{formatDateTime} Problem z wysłaniem na maile\n{str(e)}\n""")

with open ('executes.log', 'a') as file:
    if queues_with_error:
        file.write(f"""{formatDateTime}\n""")
        for queue in queues_with_error:
            file.write(f"""{queue}\n""")
    else:
        file.write(f"""{formatDateTime} - Brak błędów\n""")
