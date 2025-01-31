from datetime import datetime
import json
import pika # type: ignore
import threading
from services.payment_service import PaymentService
from repositories.payment_repository import PaymentRepository
from database.database import get_db
import uuid
from env import settings
import time
import logging
from typing import Optional
import stripe

db = get_db()
payment_repository = PaymentRepository(db)
payment_service = PaymentService(payment_repository)

stripe.api_key = settings.STRIPE_API_KEY


def callback(ch, method, properties, body):
    exchange = method.exchange
    print(f"Received payment from {exchange}: {body}")
    
    if exchange == 'HotelUp.Customer:ReservationCreatedEvent':
        create_payment(body)
    elif exchange == 'HotelUp.Customer:ReservationCanceledEvent':
        ...
        
def create_payment(body):
    message = json.loads(body)['message']
    reservation_id = message['reservationId']
    amount = int(float(message['accommodationPrice']) * 100)

    try:
        # Create Stripe session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "pln",
                    "product_data": {
                        "name": f"Rezerwacja nr: {reservation_id}",
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://localhost",
            cancel_url="https://localhost",
        )

        payment_intent_id = session.payment_intent
        
        # Store payment in database
        db = next(get_db())
        payment_repository = PaymentRepository(db)
        payment_repository.create_payment(
            reservation_id=reservation_id,
            amount=amount,
            checkout_url=session.url,
            stripe_session_id=session.id,
            payment_intent_id=payment_intent_id 
        )

        logging.info(f"Payment created for reservation {reservation_id}")
        return True

    except Exception as e:
        logging.error(f"Error creating payment: {str(e)}")
        return False
    

def connect_with_retry(max_retries=3):
    delay = 1
    credentials = pika.PlainCredentials(
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )
    
    client_properties = {
        'connection_name': 'hotelup-payment-service',
        'application': 'HotelUp Payment Service'
    }
    
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=5672,
                    credentials=credentials,
                    virtual_host='/',
                    connection_attempts=3,
                    retry_delay=2,
                    client_properties=client_properties
                )
            )
            logging.info("RabbitMQ connection established successfully")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to establish RabbitMQ connection after {max_retries} attempts: {e}")
                return None
            logging.warning(f"Connection attempt {attempt + 1} failed, retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    return None

def consume():
    connection = connect_with_retry()
    if not connection:
        logging.error("Failed to establish connection")
        return
    
    channel = connection.channel()
    
    # Declare the exchanges
    exchange_names = ['HotelUp.Customer:ReservationCreatedEvent', 
                     'HotelUp.Customer:ReservationCanceledEvent']
    for exchange_name in exchange_names:
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)
        logging.info(f"Declared exchange {exchange_name}")
    
    # Declare the queue
    queue_name = 'HotelUp.Payment:Queue'
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Bind the queue to each exchange
    for exchange_name in exchange_names:
        channel.queue_bind(exchange=exchange_name, queue=queue_name)
        print(f"Bound queue {queue_name} to exchange {exchange_name}")
    
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print('Waiting for tasks. To exit press CTRL+C')
    channel.start_consuming()

def start_consumer():
    thread = threading.Thread(target=consume)
    thread.start()