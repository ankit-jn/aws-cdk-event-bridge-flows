import json
import os

from core.utils.datetime import get_current_timestamp_string
import boto3

client = boto3.client("events")

event_bus_arn = os.getenv("EVENT_BUS_ARN")
ORDER_STAGES = ["order_receive", "order_process", "order_shipment", "order_deliver"]


def lambda_handler(event, context) -> None:
    print(event)
    
    timestamp = get_current_timestamp_string()
    print(f"Event Generator Function is triggered at {timestamp}")

    request_body = json.loads(event["body"])
    event_type = request_body["stage"]
    
    
    if event_type not in ORDER_STAGES:
        response = { "statusCode": 400, "body": "Invalid Input" }
    else:
        order_id = request_body["order_id"]
        payload = {
            "order_id": order_id,
            "order_date": timestamp
        }

        entry = {
            "Time": timestamp,
            "Source": "arjstack",
            "DetailType": event_type,
            "Detail": json.dumps(payload),
            "EventBusName": event_bus_arn,
        }

        response = client.put_events(
            Entries=[
                entry,
            ]
        )
        print(response)
        
        response = {
            "statusCode": 200,
            "body": json.dumps(response, indent=4, sort_keys=True, default=str),
        }
    
    print("Event Generator Function is executed successfully.")
    
    return response

