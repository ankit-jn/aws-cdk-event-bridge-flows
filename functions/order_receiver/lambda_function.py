import json

from core.utils.datetime import get_current_timestamp_string

def lambda_handler(event, context):

    print(event)
    
    timestamp = get_current_timestamp_string()
    print(f"Order Receiver Function is triggered at {timestamp}.")

    event_type = event.get("event_type")
    order_id = event.get("order_id")
    payload = event.get("payload")

    print(f"Event Type: {event_type}")

    print(f"Order ID: {order_id}")
    print(f"Order Details:\n {payload}")

    print("Order Receiver Function is executed successfully.")