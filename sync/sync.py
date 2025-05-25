import json
from confluent_kafka import Consumer
import requests

BASE_URL = (
    "http://statistiques-service.stats.svc.cluster.local:8005"
)  # Base URL for FastAPI microservice
KAFKA_BROKER = "kafka-service:9092"


def process_user_create(data):
    user_payload = {
        "id": str(data["userId"]),
        "name": f"{data['firstName']} {data['lastName']}",
        "gender": data["profil"]["information"]["gender"].capitalize(),
        "age": data["profil"]["information"]["age"],
        "orientation": {
            "name": data["profil"]["information"]["orientation"].capitalize()
        },
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_payload)
    if response.status_code != 200:
        print(f"Failed to create user: {response.json()}")
    else:
        print(f"User created successfully: {response.json()}")


def process_user_update(data):
    user_payload = {
        "id": str(data["userId"]),
        "name": f"{data['firstName']} {data['lastName']}",
        "gender": data["profil"]["information"]["gender"].capitalize(),
        "age": data["profil"]["information"]["age"],
        "orientation": {
            "name": data["profil"]["information"]["orientation"].capitalize()
        },
    }
    response = requests.put(
        f"{BASE_URL}/users/{data['userId']}", json=user_payload
    )
    if response.status_code != 200:
        print(f"Failed to update user: {response.json()}")
    else:
        print(f"User updated successfully: {response.json()}")


def process_user_delete(data):
    user_id = str(data["userId"])
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    if response.status_code != 200:
        print(f"Failed to delete user: {response.json()}")
    else:
        print(f"User deleted successfully: {response.json()}")


def consume_kafka_events(KAFKA_BROKER):
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BROKER,
            "group.id": "produits_service",
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe(["USER"])
    print("Starting Kafka consumer...")
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue  # No message received, continue polling
            if message.error():
                print(f"Consumer error: {message.error()}")
                continue

            # Parse the message value
            event = json.loads(message.value().decode("utf-8"))
            event_type = event.get("eventType")
            print(f"Processing event: {event_type}")

            # Handle the event based on its type
            if event_type == "USER_CREATE":
                process_user_create(event)
            elif event_type == "USER_UPDATED":
                process_user_update(event)
            elif event_type == "USER_DELETED":
                process_user_delete(event)
            else:
                print(f"Unknown event type: {event_type}")

    except KeyboardInterrupt:
        print("Consumer interrupted")
    finally:
        consumer.close()  # Ensure the consumer is properly closed


# Start consuming Kafka events
consume_kafka_events(KAFKA_BROKER=KAFKA_BROKER)
