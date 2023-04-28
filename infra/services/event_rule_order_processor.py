import json

from aws_cdk import Duration
from aws_cdk import aws_events, aws_pipes, aws_sqs
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam, aws_lambda
from aws_cdk import aws_sqs as sqs
from constructs import Construct

def create_event_rule_order_processor(
    scope: Construct,
    deployment_name: str,
    event_bus: aws_events.EventBus,
    order_processor_lambda: aws_lambda.Function,
    dead_letter_queue: sqs.Queue, 
) -> None:
    """
    Event Rule #3: All the events with event-type as "order_process" 
    """

    # SQS Queue
    order_process_queue = sqs.Queue(
        scope,
        id=f"{deployment_name}-order-process-queue",
        queue_name=f"{deployment_name}-order-process-queue",
        visibility_timeout=Duration.seconds(300),
    )
    
    event_rule = aws_events.Rule(
        scope,
        id=f"{deployment_name}-event-rule-order-processor",
        rule_name=f"{deployment_name}-event-rule-order-processor",
        description="Event Rule #3 [order-processor]",
        event_bus=event_bus,
    )
    
    event_rule.add_event_pattern(
        account=[event_bus.env.account],
        detail_type=aws_events.Match.exact_string(value="order_process"),
    )
    
    event_rule.add_target(
        target=targets.SqsQueue(
            queue=order_process_queue,
            retry_attempts=2,
            max_event_age=Duration.minutes(15),
            dead_letter_queue=dead_letter_queue,
        )
    )

    event_pipe_role = aws_iam.Role(
            scope,
            id=f"{deployment_name}-event-pipe-role",
            role_name=f"{deployment_name}-event-pipe-role",
            assumed_by=aws_iam.ServicePrincipal("pipes.amazonaws.com"),
            inline_policies={
                f"{deployment_name}-event-pipe-policy": aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "sqs:ReceiveMessage",
                                "sqs:DeleteMessage",
                                "sqs:GetQueueAttributes",
                            ],
                            resources=[order_process_queue.queue_arn],
                        ),
                        aws_iam.PolicyStatement(
                            effect=aws_iam.Effect.ALLOW,
                            actions=[
                                "lambda:InvokeFunction",
                            ],
                            resources=[order_processor_lambda.function_arn],
                        ),
                    ],
                )
            },
        )
    event_pipe = aws_pipes.CfnPipe(
        scope,
        id=f"{deployment_name}-order-processor-pipe",
        name=f"{deployment_name}-order-processor-pipe",
        role_arn=event_pipe_role.role_arn,
        source=order_process_queue.queue_arn,
        target=order_processor_lambda.function_arn,
        source_parameters=aws_pipes.CfnPipe.PipeSourceParametersProperty(
            sqs_queue_parameters=aws_pipes.CfnPipe.PipeSourceSqsQueueParametersProperty(
                batch_size=1
            )
        ),
    )
