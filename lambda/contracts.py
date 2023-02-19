import json

def handler(event, context):
    resource,method = event["resource"],event["httpMethod"]
    resources = {"resource":resource,"method":method}
    return_object = {"statusCode":200,"headers":{"Content-Type": "application/json"},"body":{} }
    try:
        if resource == "/contracts" and method == "GET":
            return_object["body"] = json.dumps({"message":"GET"})
        
        elif resource == "/contracts" and method == "POST":
            return_object["body"] = json.dumps({"message":"POST"})
        
        elif resource == "/contracts/{contract_id}" and method == "GET":
            return_object["body"] = json.dumps({"message":"GET CONTRACT"})
        
        elif resource == "/contracts/{contract_id}" and method == "DELETE":
            return_object["body"] = json.dumps({"message":"DELETE"})
        
        elif resource == "/contracts/{contract_id}" and method == "PATCH":
            return_object["body"] = json.dumps({"message":"PATCH"})
       
        else:
            return_object["body"] = json.dumps(resources)
    except Exception as error:
        return_object["statusCode"] = 400
        return_object["body"] = json.dumps({"message":str(error)})
    return return_object