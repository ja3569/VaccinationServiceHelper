import json
import boto3
import requests
from decimal import *
from botocore.exceptions import ClientError
import random

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/445215740396/vaccination_service_sqs'

def pullMessage(sqs, queue_url):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=3,
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
        )
    return response

def getMessage(response1):
    message = response1['Messages'][0]
    rh = message['ReceiptHandle']
    recipient_name = message['MessageAttributes']['RecipientName']['StringValue']
    vaccination_name = message['MessageAttributes']['VaccinationName']['StringValue']
    location = message['MessageAttributes']['Location']['StringValue']
    zip_code = message['MessageAttributes']['ZipCode']['StringValue']
    email = message['MessageAttributes']['Email']['StringValue']
    message = ["Dear {},\n Your zip code is {}. Here are the nearby vaccination centers for {}. Thanks for your patience!\n\n".format(recipient_name, zip_code, vaccination_name), str(email), str(zip_code), rh]
    return message
    
def deleteMsg(message, sqs, queue_url):
    receipt_handle = message
    response = sqs.delete_message(queue_url, ReceiptHandle=receipt_handle)
    return response
    
def pullDB(i, objectid):
    db = boto3.resource('dynamodb')
    table = db.Table('VaccinationCenter')
    response = table.get_item(Key={'objectid': objectid})["Item"]
    res = "{}. {}, located at {}, {}. Call {} to make a reservation.\n".format(i, response['facility_name'], response['address'], response['zip_code'], response['phone'])
    return res
    
def searchZipCode(zip_code):
    db = boto3.resource('dynamodb')
    table = db.Table('VaccinationCenter')
    response = table.scan()
    idList = []
    for item in response['Items']:
        if item['zip_code'] == zip_code:
            idList.append(item['objectid'])
    return idList

def lambda_handler(event=None, context=None):
    response1 = pullMessage(sqs, queue_url)
    msg = getMessage(response1)
    idList = searchZipCode(msg[2])
    messag = msg[0] + "\n"
    for i in range(len(idList)):
        messag = messag + pullDB(str(i+1), idList[i]) + "\n"
    client = boto3.client("ses", region_name="us-east-1")
    response = client.send_email(
        Destination={
            'ToAddresses': [
                msg[1],
            ],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': "UTF-8",
                    'Data': messag,
                }
            },
            'Subject': {
                'Charset': "UTF-8",
                'Data': "Vaccination Center",
            },
        },
        Source="Ari An <ja3569@columbia.edu>"
    )
    return

    

