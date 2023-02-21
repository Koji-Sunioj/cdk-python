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
    contracts_table = dynamodb.Table(os.environ['CONTRACT_TABLE'])
    shifts_table = dynamodb.Table(os.environ['SHIFTS_TABLE'])
    return_object = {"statusCode":200,"headers":{"Content-Type":
    "application/json"},"body":{}} 

    print(resource)
    
    try:
        if resource == "/contracts" and method == "GET":
            contracts = contracts_table.scan()
            return_object["body"] = json.dumps({"contracts":
            contracts["Items"]},default=serialize_float)
        
        elif resource == "/contracts" and method == "POST":
            contract = json.loads(event['body'],parse_float=Decimal)
            contract["contract_id"] = context.aws_request_id
            response = contracts_table.put_item(Item=contract)
            check_response(response,"malformed data")
            return_object["body"] = json.dumps({"message":
            "successfully created contract","contract": contract},
            default=serialize_float)
                                   
        elif resource == "/contracts/{contract_id}" and method == "GET":
            contract = contracts_table.get_item(Key={'contract_id': contract_id})
            return_object["body"] = json.dumps({"contract":
            contract["Item"]},default=serialize_float)
        
        elif resource == "/contracts/{contract_id}" and method == "DELETE":
            response = contracts_table.delete_item(Key={'contract_id': contract_id})
            check_response(response,"could not delete")
            message = "successfully deleted contract %s" % (contract_id)
            return_object["body"] = json.dumps({"message":message})            
           
        elif resource == "/contracts/{contract_id}" and method == "PATCH":
            contract = json.loads(event['body'],parse_float=Decimal)
            response = contracts_table.update_item(Key={"contract_id":contract_id},
            UpdateExpression="set base_pay=:base_pay, title=:title",
            ExpressionAttributeValues={":base_pay":contract["base_pay"],":title":contract["title"]},
            ReturnValues="ALL_NEW")
            check_response(response,"could not update")
            message = "successfully updated contract %s" % (contract_id)
            return_object["body"] = json.dumps({"message":message,"contract":response["Attributes"],
            },default=serialize_float)
        elif resource == "/contracts/{contract_id}/shifts" and method == "POST":
            shifts = json.loads(event['body'])["shifts"]
            with shifts_table.batch_writer() as batch:
                for shift in shifts:
                    shift["contract_id"] = contract_id
                    batch.put_item(Item=shift)
            message = "successfully created %s shifts under contract %s" % (len(shifts),contract_id)
            return_object["body"] = json.dumps({"message":message})

        elif resource == "/contracts/{contract_id}/shifts/{start_time}" and method == "DELETE":
            start_time = int(event["pathParameters"]["start_time"])
            response = shifts_table.delete_item(Key={'contract_id': contract_id,"start_time":start_time})
            check_response(response,"could not delete")
            message = "successfully delete shift starting at %s under contract %s" % (str(start_time),contract_id)
            return_object["body"] = json.dumps({"message":message})
        elif resource == "/contracts/{contract_id}/shifts/{start_time}" and method == "GET":
            start_time = int(event["pathParameters"]["start_time"])
            something = shifts_table.query(
            KeyConditionExpression="contract_id=:contract_id AND start_time=:start_time",
            ExpressionAttributeValues={":contract_id":contract_id,":start_time":start_time}
            )
      
            return_object["body"] = json.dumps({"shift":something["Items"]},default=serialize_float)
       
        else:
            return_object["statusCode"] = 404
            return_object["body"] = json.dumps({"message":"no matching resource"})
    
    except Exception as error:
        return_object["statusCode"] = 400
        return_object["body"] = json.dumps({"message":str(error)})
    
    return return_object