import boto3
import os

dynamodb = boto3.resource('dynamodb')
contracts_table = dynamodb.Table(os.environ['CONTRACT_TABLE'])
shifts_table = dynamodb.Table(os.environ['SHIFTS_TABLE'])


def get_contracts():
    contracts = contracts_table.scan()
    return contracts["Items"]


def put_contract(contract):
    response = contracts_table.put_item(Item=contract)
    return response


def get_contract(contract_id):
    contract = contracts_table.get_item(Key={'contract_id': contract_id})
    return contract["Item"]


def delete_contract(contract_id):
    response = contracts_table.delete_item(Key={'contract_id': contract_id})
    return response


def patch_contract(contract):
    response = contracts_table.update_item(Key={"contract_id": contract["contract_id"]},
                                           UpdateExpression="set base_pay=:base_pay, title=:title",
                                           ExpressionAttributeValues={":base_pay": contract["base_pay"],
                                           ":title": contract["title"]}, ReturnValues="ALL_NEW")
    return response


def put_shifts(contract_id, shifts):
    try:
        with shifts_table.batch_writer() as batch:
            for shift in shifts:
                shift["contract_id"] = contract_id
                batch.put_item(Item=shift)
        response_code = 200
    except:
        response_code = 400
    response = {"ResponseMetadata": {"HTTPStatusCode": response_code}}
    return response


def get_shifts(contract_id, start_time, end_time=None):
    args = dict(KeyConditionExpression="contract_id=:contract_id AND start_time>=:start_time",
                ProjectionExpression="start_time,end_time",
                ExpressionAttributeValues={":contract_id": contract_id, ":start_time": start_time})

    if end_time != None:
        args["FilterExpression"] = "end_time<=:end_time"
        args["ExpressionAttributeValues"][":end_time"] = end_time

    shifts = shifts_table.query(**args)
    return shifts["Items"]


def delete_shifts(contract_id, shifts):
    try:
        with shifts_table.batch_writer() as batch:
            for shift in shifts:
                shifts_table.delete_item(
                    Key={"contract_id": contract_id, "start_time": int(shift["start_time"])})
        response_code = 200
    except:
        response_code = 400
    response = {"ResponseMetadata": {"HTTPStatusCode": response_code}}
    return response
