from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_fn,
    aws_apigateway as apigw,
    Stack,
)

from constructs import Construct

class CdkPythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(self, "ContractsTable",
            partition_key=dynamodb.Attribute(name="contract_id", type=dynamodb.AttributeType.STRING))

        contracts_fn = lambda_fn.Function(self, "ContractsFunction",
            runtime=lambda_fn.Runtime.PYTHON_3_9,
            code=lambda_fn.Code.from_asset("lambda"),
            handler="contracts.handler",
            environment={'DB_NAME': table.table_name})

        table.grant_read_write_data(contracts_fn)

        contracts_endpoint = apigw.LambdaRestApi(
            self, 'ContractsEndpoint',
            handler=contracts_fn,
            proxy=False,
            default_method_options={"api_key_required":True}
        )

        contracts = contracts_endpoint.root.add_resource("contracts")
        contracts.add_method("GET")
        contracts.add_method("POST")

        contract = contracts.add_resource("{contract_id}")
        contract.add_method("GET")
        contract.add_method("DELETE")
        contract.add_method("PATCH")


        plan = contracts_endpoint.add_usage_plan("UsagePlan",
            name="ContractApiPlan",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            ),
            api_stages=[apigw.UsagePlanPerApiStage(stage=contracts_endpoint.deployment_stage)]
        )

        key = contracts_endpoint.add_api_key("ApiKey")
        plan.add_api_key(key)
   

       
