## ARJ-Stack: Provision solution of Serverless Messaging with EventBridge using AWS CDK

This repository is a walkthrough (along with code) on end-to-end setup of how to utilize Event Bridge service to setup serverless messaging system.<br> 

This example is using hypothetical order stages to demonstrate the different ways of using Event Bridge Service as mentioned below:

#### Source: 

API G/w -> Lambda function, which is writing events to Event Bus.

#### Targets: 

- Use of Event Bridge to send the events to CloudWatch.
  - Here, The target of the Event Rule is Cloud Watch Log Group
  - Event Pattern: All the events having detail type prefixed with `order`
  - This is the use case of logging all events prefixed with `order` to a Cloud Watch Log Group
- Use Event Bridge to set events to a lamnda function for further processing
  - Here, The target of the Event Rule is Lambda function
  - Event Pattern: All the events having detail type: `order_receive`
- Use Event Bridge to set events to a SQS queue first then with a Event pipe to a lamnda function for further processing
  - Here, The target of the Event Rule is SQS Queue piping to A lambda function
  - Event Pattern: All the events having detail type: `order_process`
- Use Event Bridge to set events to call an API for further processing
  - Here, The target of the Event Rule API Gateway
  - Event Pattern: All the events having detail type: `order_shipment`
- Use Event Bridge to set events to SQS Queue
  - Here, The target of the Event Rule is SQS Queue
  - Event Pattern: All the events having detail type: `order_deiver`

#### Reference Diagram

<img src="https://github.com/ankit-jn/aws-cdk-event-bridge-flows/blob/main/image/design.jpg">

- There are other Source/Target combinations available that can effectivey be used based on requirements.

#### How to Test?

Hit the API with following json in request body:

- API: https://<API ID>.execute-api.<AWS Region Code>.amazonaws.com/dev/events/generator
- Method: Post
- Request Body (Json):
```
{
	"stage": "order_process",
	"order_id": 14
}
```

- Reference values for stage: `order_receive`, `order_process`, `order_shipment1, `order_deliver`

### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_awscli"></a> [awscli](#requirement\_awscli) | 2.9.21 |
| <a name="requirement_python"></a> [python](#requirement\_python) | 3.11.1 |
| <a name="requirement_poetry"></a> [poetry](#requirement\_poetry) | 1.4.1 |

### Pre-requisites?

There are few steps that we need to follow to setup/configure the environment on local system. Refer [AWS Cloud Development Kit (AWS CDK) - Setup](https://github.com/ankit-jn/devops-aws-cdk-setup) for detailed instruction.

### How to setup the project (if doing it from start rather cloning it)

- Create a directory named `aws-cdk-event-bridge-flow`
- Run the following commands withint the directory:

```
poetry init
poetry add antlr4-python3-runtime
poetry add pytest
```

### How to run it?

#### Create Python Virual Environment 

Run the following command to create python virual environment:

```
python -m venv .venv
```

#### Activate/Prapare the environment

Run the following command to activate the virtualenv:

```
.venv\Scripts\activate.bat
```

Run the following command to prepare the virtualenv for CDK references:

```
python -m pip install aws-cdk-lib 
```

#### Delete the executable directory (if any)

```
rmdir /S layer
```

#### Setup the executable directory

```
mkdir layer\python
xcopy core layer\python\core /E/H
```

#### Export dependencies

```
poetry export --without-hashes --format=requirements.txt > requirements-poetry.txt
```

#### Install dependencies

```
python -m pip install -r requirements-poetry.txt --target .\layer\python\ --upgrade
```

#### Synthesize the stack

```
cdk synth --profile <AWS Credential Profile Name>
```

#### Stack deployment

```
cdk deploy --profile <AWS Credential Profile Name>
```

### Authors

Module is maintained by [Ankit Jain](https://github.com/ankit-jn) with help from [these professional](https://github.com/ankit-jn/aws-cdk-event-bridge-flow/graphs/contributors).
