from datetime import datetime
from http.client import responses
from urllib import response
from django.apps import AppConfig
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
import traceback
import logging
import mysql.connector



class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'oatmas-ebag-770f6996a797.json'
DIALOGFLOW_PROJECT_ID = 'oatmas-ebag'
DIALOGFLOW_LANGUAGE_CODE = 'en'


@require_http_methods(['GET','POST'])
@csrf_exempt
def webhook(request):
    try:
        newjsonData = json.loads(request.body)
        query_result = newjsonData.get('queryResult')
        global responseText
        responseText = ""
    
        # connect db with django
        mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "oatmas"
        )  

        # Intent: Welcome - no
        # Context: awaiting_registry
        if query_result.get('action') == 'Welcome.Welcome-no':
            
            buyer = str(query_result.get('parameters').get('buyer'))
            address = str(query_result.get('parameters').get('address'))
            global phoneNo
            phoneNo = str(query_result.get('parameters').get('phoneNo'))

            mycursor = mydb.cursor()

            # insert data into Oatmas Database

            # table: Customer
            sql = "INSERT INTO customer (phoneNo, name, address) VALUES (%s, %s, %s)"
            val = (phoneNo, buyer, address)
            mycursor.execute(sql, val)

            mydb.commit()
        
            print(mycursor.rowcount, "record registered customer inserted.")
            mycursor.close()

        # Intent: enquiry - no
        # Context: awaiting_registry  
        if query_result.get('action') == 'enquiryNo':
            car_model = str(query_result.get('parameters').get('car_model'))
            car_parts = str(query_result.get('parameters').get('car_parts'))
            mycursor = mydb.cursor()

            # table: Enquiry_log
            sql = "INSERT INTO enquiry_log (date, model, parts, phoneNo)" "VALUES (%s, %s, %s, %s)"
            date = datetime.now()
            now = date.strftime('%Y-%m-%d')
            val = (now, car_model, car_parts, phoneNo)
            mycursor.execute(sql, val)

            mydb.commit()
            
            print(mycursor.rowcount, "record enquiry log and details inserted.")

            mycursor.close()

            
        # Intent: Welcome - yes
        # Context: awaiting_enquiry
        if query_result.get('action') == 'Welcome.Welcome-yes':
            
            global phoneNo2
            phoneNo2 = str(query_result.get('parameters').get('phoneNo'))
            global fetchBuyer, fetchAddress
            mycursor = mydb.cursor()

            # table: Customer, fetch buyer name
            sql = "SELECT name FROM customer WHERE phoneNo = (%s)"
            val = (phoneNo2,)
            mycursor.execute(sql, val)
            fetchBuyer = mycursor.fetchone()
            print(fetchBuyer)
            
            # table: Customer, fetch buyer address
            sql = "SELECT address FROM customer WHERE phoneNo = (%s)"
            val = (phoneNo2,)
            mycursor.execute(sql, val)
            fetchAddress = mycursor.fetchone()
            print(fetchAddress)


        # Intent: enquiry - yes
        # Context: awaiting_enquiry
        if query_result.get('action') == 'enquiryYes':
            
            mycursor = mydb.cursor()
            car_model = str(query_result.get('parameters').get('car_model'))
            vin_chassis = str(query_result.get('parameters').get('vin_chassis'))
            engine_no = str(query_result.get('parameters').get('engine_no'))
            car_parts = str(query_result.get('parameters').get('car_parts'))
            urgency = str(query_result.get('parameters').get('urgency'))
            quality = str(query_result.get('parameters').get('quality'))
            quantity = str(query_result.get('parameters').get('qty'))

            #insert data to db
            # table: Enquiry_log
            sql = "INSERT INTO enquiry_log (date, model, parts, phoneNo)" "VALUES (%s, %s, %s, %s)"
            date = datetime.now()
            now = date.strftime('%Y-%m-%d')
            val = (now, car_model, car_parts, phoneNo2)
            mycursor.execute(sql, val)

            mydb.commit()
            
            print(mycursor.rowcount, "record enquiry log and details inserted.")

            mycursor.close()
            
            responseText = fetchBuyer[0] + "'s Inquiry\n" + "\nModel: " + car_model + "\nChassis: " + vin_chassis + "\n\nPart(s): " + car_parts + "\nQuality:" + quality + "\nQuantity" + quantity + "\nAddress: " + fetchAddress[0]
            #responseText = "Hi this is a reply from fulfillment"

            print(responseText)

            newjsonData = {"fulfillmentMessages": [{"text": {"text": [responseText]}}]}

            print(JsonResponse(newjsonData).content)

        return JsonResponse(newjsonData)

    except Exception as e:
        print(e)
        logging.error(traceback.format_exc())
        return HttpResponse("Error.")