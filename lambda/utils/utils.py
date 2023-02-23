from decimal import Decimal
from datetime import datetime 

def serialize_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)

def serialize_int(obj):
    if isinstance(obj, Decimal):
        return int(obj)

def epoch_to_date(epoch):
    return datetime.utcfromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

def check_response(response,message):
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise Exception(message) 