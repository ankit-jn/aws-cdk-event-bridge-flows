import json

from core.utils.datetime import get_current_timestamp_string

def lambda_handler(event, context):
    print(event)
    
    timestamp = get_current_timestamp_string()
    print(f"Order Processor Function is triggered at {timestamp}.")
    
    request_body = json.loads(event[0].get("body"))
    event_type = request_body.get("detail-type")
    payload = request_body.get("detail")

    print(f"Event Type: {event_type}")

    print(f"Order Details:\n {payload}")

    print("Order Processor Function is executed successfully.")