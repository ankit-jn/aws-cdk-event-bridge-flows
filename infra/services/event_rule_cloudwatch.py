from aws_cdk import aws_events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sqs as sqs
from constructs import Construct

def create_event_rule_cloudWatch(
    scope: Construct,
    deployment_name: str,
    event_bus: aws_events.EventBus,
    events_log_group: logs.LogGroup,
    dead_letter_queue: sqs.Queue,
) -> None:
    """
    Event Rule #1 [CloudWatch]: All events logged to CloudWatch Log Group
    """
    event_rule = aws_events.Rule(
        scope,
        id=f"{deployment_name}-event-rule-cloudwatch",
        rule_name=f"{deployment_name}-event-rule-cloudwatch",
        description="Event Rule #1 [CloudWatch]",
        event_bus=event_bus,
    )
    # All the events with the current AWS account number
    event_rule.add_event_pattern(
        account=[event_bus.env.account],
        detail_type=aws_events.Match.prefix(value="order"),
    )

    event_rule.add_target(
        target=targets.CloudWatchLogGroup(
            log_group=events_log_group,
            dead_letter_queue=dead_letter_queue,
        )
    )
