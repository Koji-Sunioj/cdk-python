from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_fn,
    aws_apigateway as apigw,
    Stack,
)
import aws_cdk as core

from constructs import Construct


class CdkPythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        contract_table = dynamodb.Table(
            self, "ContractsTable",
            partition_key=dynamodb.Attribute(
                name="contract_id",
                type=dynamodb.AttributeType.STRING))

        shifts_table = dynamodb.Table(
            self, "ShiftsTable",
            partition_key=dynamodb.Attribute(
                name="contract_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name="start_time",
                type=dynamodb.AttributeType.NUMBER))

        lambda_layer = lambda_fn.LayerVersion(
            self, 'LambdaLayer',
            code=lambda_fn.AssetCode('layer/'),
            compatible_runtimes=[lambda_fn.Runtime.PYTHON_3_8],
        )

        contracts_fn = lambda_fn.Function(
            self, "ContractsFunction",
            layers=[lambda_layer],
            runtime=lambda_fn.Runtime.PYTHON_3_8,
            code=lambda_fn.Code.from_asset(
                "lambda"
            ),
            handler="contracts.handler",
            environment={'CONTRACT_TABLE': contract_table.table_name,
                         "SHIFTS_TABLE": shifts_table.table_name})

        contract_table.grant_read_write_data(contracts_fn)
        shifts_table.grant_read_write_data(contracts_fn)

        contracts_endpoint = apigw.LambdaRestApi(
            self, 'ContractsEndpoint',
            handler=contracts_fn,
            proxy=False,
            default_method_options={"api_key_required": True}
        )

        contracts = contracts_endpoint.root.add_resource("contracts")
        contracts.add_method("GET")
        contracts.add_method("POST")

        contract = contracts.add_resource("{contract_id}")
        contract.add_method("GET")
        contract.add_method("DELETE")
        contract.add_method("PATCH")

        shifts = contract.add_resource("shifts")
        shifts.add_method("POST")

        start = shifts.add_resource("{start_time}")
        end = start.add_resource("{end_time}")
        end.add_method("DELETE")
        end.add_method("GET")

        user_aggregate = contracts_endpoint.root.add_resource("aggregate-user")
        user_wages = user_aggregate.add_resource("{user_name}")
        user_wages.add_method("GET")

        contract_aggregate = contracts_endpoint.root.add_resource(
            "aggregate-contract")
        contract_wages = contract_aggregate.add_resource("{contract_id}")
        contract_wages.add_method("GET")

        plan = contracts_endpoint.add_usage_plan(
            "UsagePlan", name="ContractApiPlan",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            ),
            api_stages=[apigw.UsagePlanPerApiStage(
                stage=contracts_endpoint.deployment_stage)]
        )

        key = contracts_endpoint.add_api_key("ApiKey")
        plan.add_api_key(key)
