import aws_cdk as core
import aws_cdk.assertions as assertions

from infra.infra_stack import InfraStack


def test_infra_created():
    app = core.App()
    stack = InfraStack(app, "infra")
    template = assertions.Template.from_stack(stack)
