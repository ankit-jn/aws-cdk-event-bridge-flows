import json

from core.utils.datetime import get_current_timestamp_string

def lambda_handler(event, context):

    print(event)
    
    timestamp = get_current_timestamp_string()
    print(f"Order Shipment Function is triggered at {timestamp}.")
    
    request_body = json.loads(event.get("body"))
    
    event_type = request_body.get("event_type")
    order_id = request_body.get("order_id")
    payload = request_body.get("payload")

    print(f"Event Type: {event_type}")

    print(f"Order ID: {order_id}")
    print(f"Order Details:\n {payload}")

    print("Order Shipment Function is executed successfully.")