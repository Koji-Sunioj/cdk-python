import json
import pkgutil
import boto3
import os
from decimal import Decimal
from utils.db_functions import (get_contracts,put_contract,get_contract,
delete_contract,patch_contract,put_shifts,get_shifts,delete_shifts)
from utils.utils import (serialize_float,serialize_int,epoch_to_date,
check_response)

def handler(event, context):
    if event["pathParameters"] != None and "contract_id" in event["pathParameters"]:
        contract_id = event["pathParameters"]["contract_id"]
    resource,method = event["resource"],event["httpMethod"]
    dynamodb = boto3.resource('dynamodb')
    contracts_table = dynamodb.Table(os.environ['CONTRACT_TABLE'])
    shifts_table = dynamodb.Table(os.environ['SHIFTS_TABLE'])
    return_object = {"statusCode":200,"headers":{"Content-Type":
    "application/json"},"body":{}} 

    try:
        if resource == "/contracts" and method == "GET":
            contracts = get_contracts()
            return_object["body"] = json.dumps({"contracts":
            contracts},default=serialize_float)
        
        elif resource == "/contracts" and method == "POST":
            contract = json.loads(event['body'],parse_float=Decimal)
            contract["contract_id"] = context.aws_request_id
            response = put_contract(contract)
            check_response(response,"malformed data")
            return_object["body"] = json.dumps({"message":
            "successfully created contract","contract": contract},
            default=serialize_float)
                                   
        elif resource == "/contracts/{contract_id}" and method == "GET":
            contract = get_contract(contract_id)
            return_object["body"] = json.dumps({"contract":contract},default=serialize_float)
        
        elif resource == "/contracts/{contract_id}" and method == "DELETE":
            response = delete_contract(contract_id)
            check_response(response,"could not delete")
            message = "successfully deleted contract %s" % (contract_id)
            return_object["body"] = json.dumps({"message":message})            
           
        elif resource == "/contracts/{contract_id}" and method == "PATCH":
            contract = json.loads(event['body'],parse_float=Decimal)
            contract["contract_id"] = contract_id
            response = patch_contract(contract)
            check_response(response,"could not update")
            message = "successfully updated contract %s" % (contract_id)
            return_object["body"] = json.dumps({"message":message,"contract":response["Attributes"],
            },default=serialize_float)
        
        elif resource == "/contracts/{contract_id}/shifts" and method == "POST":
            shifts = json.loads(event['body'])["shifts"]
            response = put_shifts(contract_id,shifts)
            check_response(response,"could not create shifts")
            message = "successfully created %s shifts under contract %s" % (len(shifts),contract_id)
            return_object["body"] = json.dumps({"message":message})

        elif resource == "/contracts/{contract_id}/shifts/{start_time}/{end_time}" and method == "DELETE":
            start_time,end_time = int(event["pathParameters"]["start_time"]),int(event["pathParameters"]["end_time"])
            shifts = get_shifts(contract_id,start_time,end_time)
            response = delete_shifts(contract_id,shifts)
            check_response(response,"could not delete shifts")
            message = "successfully deleted %s shifts starting %s and ending %s under contract %s" % (len(shifts),epoch_to_date(start_time),epoch_to_date(end_time),contract_id)
            return_object["body"] = json.dumps({"message":message})
        
        elif resource == "/contracts/{contract_id}/shifts/{start_time}/{end_time}" and method == "GET":
            start_time,end_time = int(event["pathParameters"]["start_time"]),int(event["pathParameters"]["end_time"])
            shifts = get_shifts(contract_id,start_time,end_time)
            return_object["body"] = json.dumps({"shifts":shifts},default=serialize_int)
       
        else:
            return_object["statusCode"] = 404
            return_object["body"] = json.dumps({"message":"no matching resource"})
    
    except Exception as error:
        return_object["statusCode"] = 400
        return_object["body"] = json.dumps({"message":str(error)})
    
    return return_object