import pika # type: ignore
import json
from env import settings

def send_message(exchange_name, routing_key, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST, 
        credentials=pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD),
        port=5672))
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    # Convert the message to JSON
    message_json = json.dumps(message)

    # Publish the message to the exchange
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message_json)
    print(f" [x] Sent {message_json}")

    # Close the connection
    connection.close()