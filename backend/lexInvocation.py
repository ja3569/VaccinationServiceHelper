import json
import math
import datetime
import logging
import boto3
import os
import time
import dateutil.parser


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helper functions --- """
def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

#Location, Cuisine, Dining Time, Number of people, Phone number
def validate_vaccination_location(intent_request):
    recipient_name = intent_request["RecipientName"]
    vaccination_name = intent_request["VaccinationName"]
    location = intent_request["Location"]
    zip_code = intent_request["ZipCode"]
    email = intent_request["Email"]
    
    if location is not None:
        if location.lower() not in ['manhattan', 'uptown', 'downtown', 'midtown', 'bronx', 'brooklyn', 'queens', 'nyc', 'new york']:
            return build_validation_result(False,
                                           'Location',
                                           '{} is out of service, please enter a location inside NYC, such as Manhattan'.format(location))
                                           
    if vaccination_name is not None:
        if vaccination_name.lower() not in ['influenza', "flu shot", "flu"]:
            return build_validation_result(False,
                                           'VaccinationName',
                                           '{} is not yet available, please enter another vaccine name, such as influenza'.format(vaccination_name))
     
    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """

def greetings(intent_request):
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi there, how can I help?'})
    

def vaccination_location(intent_request):
    recipient_name = get_slots(intent_request)["RecipientName"]
    vaccination_name = get_slots(intent_request)["VaccinationName"]
    location = get_slots(intent_request)["Location"]
    zip_code = get_slots(intent_request)["ZipCode"]
    email = get_slots(intent_request)["Email"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_vaccination_location(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
        return delegate(intent_request['sessionAttributes'], get_slots(intent_request))
    
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/445215740396/vaccination_service_sqs'
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageAttributes={
           'RecipientName': {
                'DataType': 'String',
                'StringValue': recipient_name
            },
            'VaccinationName': {
                'DataType': 'String',
                'StringValue': vaccination_name
            },
            'Location': {
                'DataType': 'String',
                'StringValue': location
            },
            'ZipCode' : {
                'DataType': 'String',
                'StringValue': zip_code
            },
            'Email': {
                'DataType': 'String',
                'StringValue': email
            }
        },
        MessageBody=('vaccination_service_sqs')
    )
    return close(intent_request['sessionAttributes'], 'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'All set! We will send you nearby locations for {} vaccination available on {} (zip code: {})'.format(vaccination_name, location, zip_code)})

    
""" --- Intents --- """


def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'GreetingIntent':
        return greetings(intent_request)
    elif intent_name == 'VaccinationLocationIntent':
        return vaccination_location(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):

    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)

