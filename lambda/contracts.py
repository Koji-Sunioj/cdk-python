import json
from decimal import Decimal
from utils.db_functions import (
    get_contracts, put_contract, get_contract, delete_contract, patch_contract,
    put_shifts, get_shifts, delete_shifts)
from utils.utils import (
    serialize_float, serialize_int, epoch_to_date, check_response)

import pandas as pd
import numpy as np


def handler(event, context):
    params = event["pathParameters"]
    if params != None and "contract_id" in params:
        contract_id = params["contract_id"]
    route_key = "%s %s" % (event["resource"], event["httpMethod"])
    response = {"statusCode": 200, "headers": {
        "Content-Type": "application/json"}, "body": {}}

    print(route_key)

    try:
        if route_key == "/contracts GET":
            contracts = get_contracts()
            response["body"] = json.dumps(
                {"contracts": contracts}, default=serialize_float)

        elif route_key == "/contracts POST":
            contract = json.loads(event['body'], parse_float=Decimal)
            contract["contract_id"] = context.aws_request_id
            table_response = put_contract(contract)
            check_response(table_response, "malformed data")
            response["body"] = json.dumps(
                {"message": "successfully created contract",
                 "contract": contract}, default=serialize_float)

        elif route_key == "/contracts/{contract_id} GET":
            contract = get_contract(contract_id)
            response["body"] = json.dumps(
                {"contract": contract}, default=serialize_float)

        elif route_key == "/contracts/{contract_id} DELETE":
            table_response = delete_contract(contract_id)
            check_response(table_response, "could not delete")
            shifts = get_shifts(contract_id, 0)
            if len(shifts) > 0:
                delete_shifts(contract_id, shifts)
            message = "successfully deleted contract %s" % (contract_id)
            response["body"] = json.dumps({"message": message})

        elif route_key == "/contracts/{contract_id} PATCH":
            contract = json.loads(event['body'], parse_float=Decimal)
            contract["contract_id"] = contract_id
            table_response = patch_contract(contract)
            check_response(table_response, "could not update")
            message = "successfully updated contract %s" % (contract_id)
            response["body"] = json.dumps(
                {"message": message, "contract": table_response["Attributes"]},
                default=serialize_float)

        elif route_key == "/contracts/{contract_id}/shifts POST":
            shifts = json.loads(event['body'])["shifts"]
            put_shifts(contract_id, shifts)
            message = "successfully created %s shifts under contract %s" % (
                len(shifts), contract_id)
            response["body"] = json.dumps({"message": message})

        elif (route_key ==
              "/contracts/{contract_id}/shifts/{start_time}/{end_time} DELETE"):
            start_time, end_time = int(
                params["start_time"]), int(params["end_time"])
            shifts = get_shifts(contract_id, start_time, end_time)
            delete_shifts(contract_id, shifts)
            message = "successfully deleted %s shifts starting %s and ending\
            %s under contract %s" % (len(shifts), epoch_to_date(start_time),
                                     epoch_to_date(end_time), contract_id)
            response["body"] = json.dumps({"message": message})

        elif (route_key ==
              "/contracts/{contract_id}/shifts/{start_time}/{end_time} GET"):
            start_time, end_time = int(
                params["start_time"]), int(params["end_time"])
            shifts = get_shifts(contract_id, start_time, end_time)
            response["body"] = json.dumps(
                {"shifts": shifts}, default=serialize_int)
        elif (route_key == "/aggregate-contract/{contract_id} GET"):
            contract = get_contract(contract_id)
            shifts = get_shifts(contract_id, 0)
            days = pd.DataFrame(shifts)
            days = days[['start_time', 'end_time']].astype(int)
            for column in days.columns:
                days[column] = pd.to_datetime(days[column], unit='s').dt.tz_localize(
                    'UTC').dt.tz_convert(contract["time_zone"]).dt.tz_localize(None)
            days["hours"] = (days["end_time"] -
                             days["start_time"]).astype('timedelta64[h]')
            days["wages"] = days["hours"] * float(contract["base_pay"])
            days.index = days["start_time"].dt.normalize()
            wages = days[["wages"]].resample(contract["pay_date"]).sum()
            wages = wages.reset_index()
            wages["start_time"] = wages.start_time.astype(str)
            table = wages.rename(columns={"start_time": "pay period"}).round(
                2).to_dict("records")
            response["body"] = json.dumps(
                {"data": table}, default=serialize_float)

        else:
            response["statusCode"] = 404
            response["body"] = json.dumps(
                {"message": "no matching resource"})

    except Exception as error:
        response["statusCode"] = 400
        response["body"] = json.dumps({"message": str(error)})

    return response
