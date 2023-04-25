#!/usr/bin/env python3
import json

import aws_cdk as cdk

from infra.infra_stack import InfraStack
from configs.deployment_config import DeploymentConfig

app = cdk.App()
app_configs = json.load(open("configs/app_configs.json"))

app_name = app.node.try_get_context("app_name")
env_name = app.node.try_get_context("environment")
app_parameters = app_configs[env_name]

configs = DeploymentConfig(app_name, env_name, app_parameters)

aws_account_id=app_parameters["account_id"]
aws_region=app_parameters["aws_region"]

deployment_env = cdk.Environment(account=aws_account_id, region=aws_region)

InfraStack(app, "InfraStack", configs=configs, env=deployment_env)

app.synth()