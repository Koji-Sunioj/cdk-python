import json
import pkgutil
import boto3
import os
from decimal import Decimal
from utils.serialize import serialize_float
from utils.check_response import check_response

def handler(event, context):
    if event["pathParameters"] != None and "contract_id" in event["pathParameters"]:
        contract_id = event["pathParameters"]["contract_id"]
    resource,method = event["resource"],event["httpMethod"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_NAME'])
    return_object = {"statusCode":200,"headers":{"Content-Type":
    "application/json"},"body":{}} 
    
    try:
        if resource == "/contracts" and method == "GET":
            contracts = table.scan()
            return_object["body"] = json.dumps({"contracts":
            contracts["Items"]},default=serialize_float)
        
        elif resource == "/contracts" and method == "POST":
            contract = json.loads(event['body'],parse_float=Decimal)
            contract["contract_id"] = context.aws_request_id
            response = table.put_item(Item=contract)
            check_response(response,"malformed data")
            return_object["body"] = json.dumps({"message":
            "successfully created contract","contract": contract},
            default=serialize_float)
                                   
        elif resource == "/contracts/{contract_id}" and method == "GET":
            contract = table.get_item(Key={'contract_id': contract_id})
            return_object["body"] = json.dumps({"contract":
            contract["Item"]},default=serialize_float)
        
        elif resource == "/contracts/{contract_id}" and method == "DELETE":
            response = table.delete_item(Key={'contract_id': contract_id})
            check_response(response,"could not delete")
            message = "successfully deleted contract %s" % (contract_id)
            return_object["body"] = json.dumps({"message":message})            
           
        elif resource == "/contracts/{contract_id}" and method == "PATCH":
            contract = json.loads(event['body'],parse_float=Decimal)
            response = table.update_item(Key={"contract_id":contract_id},
            UpdateExpression="set base_pay=:base_pay, title=:title",
            ExpressionAttributeValues={":base_pay":contract["base_pay"],":title":contract["title"]},
            ReturnValues="ALL_NEW")
            check_response(response,"could not update")
            message = "successfully updated contract %s" % (contract_id)
            return_object["body"] = json.dumps({"message":message,"contract":response["Attributes"],
            },default=serialize_float)
       
        else:
            return_object["statusCode"] = 404
            return_object["body"] = json.dumps({"message":"no matching resource"})
    
    except Exception as error:
        return_object["statusCode"] = 400
        return_object["body"] = json.dumps({"message":str(error)})
    
    return return_object