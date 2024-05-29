from api import apikey
from flask import Flask, request, jsonify
import pandas as pd
from csv import writer
import re
import os
import time
import openai
import json
import jsonpickle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pdf_gen import InvoiceGenerator
apikeys = apikey

app = Flask(__name__)


############## GPT PROMPT ####################
def gpt(inp):
    systems = {"role":"system","content":"""
              you are a AI assistant you are developed by team of developers in proxima AI Co.
               you're task is to assist the user in anyway he want.
               if someone ask you to generate invoice you have to collect information one by one 'one question at a time'
               company name, number of Items with there quantity, and price, client name,his address, client email,client_address,currency, any note he would like to add
               and his bank account details one by one.
               ask every question one by one in single turn.ask only one question at a time is important.
               when you get all the answer make a Json of it and return it inside '``' dont reply with any message while generating json. 
               see example make sure the json should be exact like that
               ```
              {
                "company_name": "Proxima AI",
                "items": [
                    {
                    "name": "Mobile app",
                    "quantity": 1,
                    "price": 2000
                    },
                    {
                    "name": "SEO",
                    "quantity": 1,
                    "price": 1000
                    }
                ],
               "client_address":"Lahore",
                "client_name": "Contegris",
                "client_phone":"+923106514851",
                "company_address": "ICCBS Karachi",
                "client_email": "contegris@gmail.com",
                "bank":"State Bank , Karachi Branch",
                "account_number" :5645135485454",
                "note":"This is the note I want to share",
                "currency":"$"
                }
               ```
               else just give some finace advise to user. 
    
    """}
    new_inp = inp
    new_inp.insert(0,systems)
    print("inp : \n ",new_inp)
    openai.api_key = apikeys
    completion = openai.ChatCompletion.create(
    model="gpt-4", 
    messages=new_inp
    )
    return completion

############    GET CHATS BY USER ID ##################
def get_chats(id):
    path = str(os.getcwd())+'\\chats\\'+id+'.json'
    isexist = os.path.exists(path)
    if isexist:
        data = pd.read_json(path)
        chats = data.chat
        return  list(chats)
    else:
        return "No Chat found on this User ID."





############### APPEND NEW CHAT TO USER ID JSON FILE #################
def write_chat(new_data, id):
    with open("chats/"+id+".json",'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["chat"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

################################################################### handle string to json
def fetch_json(input_string):
    # Regular expression pattern to find JSON between backticks
    pattern = r'`([^`]+)`'
    
    # Search for the pattern in the input string
    match = re.search(pattern, input_string)
    
    if match:
        json_string = match.group(1)
        try:
            json_object = json.loads(json_string)
            return json_object
        except json.JSONDecodeError:
            print("Error: The extracted string is not valid JSON.")
            return None
    else:
        print("No JSON string found in the input.")
        return None
# {
#                 "company_name": "Proxima AI",
#                 "items": [
#                     {
#                     "name": "Mobile app",
#                     "quantity": 1,
#                     "price": 2000
#                     },
#                     {
#                     "name": "SEO",
#                     "quantity": 1,
#                     "price": 1000
#                     }
#                 ],
                # "client_address":"Lahore"
#                 "client_name": "Contegris",
#                 "company_address": "ICCBS Karachi",
#                 "client_email": "contegris@gmail.com"
#                 }
#################################################################### handle JSON to invoice
def invoice(data, output_filename="invoice.pdf"):
    comp_name = data['company_name']
    items =data['items']
    client_name = data['client_name']
    company_address = data['company_address']
    client_email = data['client_email']
    client_address = data['client_address']
    bank = data['bank']
    note = data['note']
    accountnumber = data['account_number']
    currency = data['currency']



    invoice = InvoiceGenerator(
        company_name=comp_name,
        recipientName=client_name,
        itemlist=items,
        companyStreetAddress=company_address,
        email=client_email,
        customerStreetAddress=client_address,
        bankname=bank,
        notes=note,
        accountnumber=accountnumber,

        currency=currency,
  
        accountname="Meezan Bank",

                               )
    invoice.call()


################################ CHECK IF USER IS ALREADY EXIST IF NOT CREATE ONE ELSE RETURN GPT REPLY ##################
@app.route('/chat', methods=['POST'])
def check_user():
    
    ids = request.json['user_id']
    prompt = request.json['prompt']
    print("asd")
    path = str(os.getcwd())+'\\chats\\'+ids+'.json'
    # path = str(os.getcwd())+'\\'+"5467484.json"
    isexist = os.path.exists(path)
    if isexist:
        # try:
        print(path," found!")
        write_chat({"role":"user","content":prompt},ids)
        # print()
        chats = get_chats(ids)
        print(chats)
        send = gpt(chats)
        reply = send.choices[0].message
        print("reply    ",reply.content)
        write_chat({"role":"assistant","content":reply.content},ids)
        if "``"  in reply.content:
            print('json found')
            fetch = fetch_json(reply.content)
            if fetch != None:
                invoices = invoice(fetch)
                return {'message':"invoice generated","status":"ok","filename":"invoice.pdf"}
            else:
                print(fetch)
                return {'message':'Please Type Generate `Try Again`'}
        else:
            print('no json found')
            return {"message":reply,"status":"OK"}
        # except:
        #     return {"message":"something went wrong!","status":"404"}

    else:
        print(path," Not found!")
        dictionary = {
        "user_id":ids,
        "chat":[]


        }
        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        
        # Writing to sample.json
        with open(path, "w") as outfile:
            outfile.write(json_object)
        reply = check_user()
        return reply

####################   NEW ENPOINT GET CHATS ##############################
@app.route('/get_chats', methods=['POST'])
def get_chatss():
    ids = request.json['user_id']
    return jsonpickle.encode(get_chats(ids))

######################################################### clear chats
@app.route('/delete_chats', methods=['POST'])
def clear_chatss():
    ids = request.json['user_id']

    try:
        path =os.remove(str(os.getcwd())+'\\chats\\'+ids+'.json')
     
        return {"status":"OK","message":"success"}
 
    except :
        return { "status":"error","message":"Something went wrong,chat doesn't exist" }

@app.route('/')
def home():
    return 'chatbot is up'

if __name__ == '__main__':
    app.run(port=5002,host="0.0.0.0")
    
