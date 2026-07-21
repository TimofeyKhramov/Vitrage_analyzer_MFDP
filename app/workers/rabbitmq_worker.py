import json
import logging

import pika

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def callback(ch, method, properties, body):

    message = json.loads(body)

    document_id = message["document_id"]

    logger.info(
        f"Received document: {document_id}"
    )

    ch.basic_ack(
        delivery_tag=method.delivery_tag,
    )


def main():

    credentials = pika.PlainCredentials(
        settings.rabbitmq_user,
        settings.rabbitmq_password,
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
        )
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=settings.rabbitmq_queue,
        durable=True,
    )

    channel.basic_qos(
        prefetch_count=1,
    )

    channel.basic_consume(
        queue=settings.rabbitmq_queue,
        on_message_callback=callback,
    )

    logger.info("RabbitMQ worker started")

    channel.start_consuming()


if __name__ == "__main__":
    main()