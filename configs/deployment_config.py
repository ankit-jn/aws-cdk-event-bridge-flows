from typing import Dict

class DeploymentConfig(object):

    def __init__(self, app_name: str, app_environment: str, app_parameters: Dict):
        self.app_name = app_name
        self.app_environment = app_environment
        self.deployment_name = f'{app_name}-{app_environment}'
        self.app_parameters = app_parameters
