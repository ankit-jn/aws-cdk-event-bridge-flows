from aws_cdk import Duration
from aws_cdk import aws_apigateway, aws_iam
from constructs import Construct

from configs.deployment_config import DeploymentConfig
from infra.services.function_service import FunctionService

FUNCTIONS_SOURCE_PATH = "../../functions"
DEFAULT_LAMBDA_TIMEOUT = Duration.seconds(15)
DEFAULT_LAMBDA_MEMORY_USAGE = 512

class ApiService(Construct):

    def __init__(
        self,
        scope: Construct,
        configs: DeploymentConfig,
        function_service: FunctionService,
        **kwargs,
    ) -> None:
        super().__init__(scope, f"{configs.deployment_name}-api")
    
        # API Gateway
        self.api = aws_apigateway.RestApi(
            self,
            id=f"{configs.deployment_name}-event-api",
            policy=aws_iam.PolicyDocument(
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        principals=[aws_iam.AnyPrincipal()],
                        actions=["execute-api:Invoke"],
                        resources=["execute-api:/*/*/*"],
                    ),
                ]
            ),
            deploy_options=aws_apigateway.StageOptions(stage_name="dev"),
        )

        event_resource = self.api.root.add_resource("events")

        event_generator_resource = event_resource.add_resource("generator")

        event_generator_lambda_integration = aws_apigateway.LambdaIntegration(
            handler=function_service.event_generator_lambda
        )

        event_generator_resource.add_method(
            http_method="POST",
            integration=event_generator_lambda_integration,
        )

        event_processor_resource = event_resource.add_resource("shipment")

        event_processor_lambda_integration = aws_apigateway.LambdaIntegration(
            handler=function_service.event_processor_lambda
        )

        event_processor_resource.add_method(
            http_method="POST",
            integration=event_processor_lambda_integration,
        )
