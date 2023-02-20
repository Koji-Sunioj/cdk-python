def check_response(response,message):
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise Exception(message) 