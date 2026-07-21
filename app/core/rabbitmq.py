import json
from uuid import UUID

import pika

from app.core.config import settings


class RabbitMQClient:

    def __init__(self):

        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password,
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials,
            )
        )

        self.channel = self.connection.channel()

        self.channel.queue_declare(
            queue=settings.rabbitmq_queue,
            durable=True,
        )

    def publish_document(
        self,
        document_id: UUID,
    ) -> None:

        body = json.dumps(
            {
                "document_id": str(document_id),
            }
        )

        self.channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

    def close(self):

        if self.connection.is_open:
            self.connection.close()