import json
import logging
from uuid import UUID

import pika
from sqlmodel import Session

from app.core.config import settings
from app.core.database import engine
from app.models.document import Document, DocumentStatus
from app.services.analysis_service import AnalysisService
from app.services.result_service import ResultService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def callback(ch, method, properties, body):

    message = json.loads(body)

    document_id = UUID(message["document_id"])

    selected_pages = message.get("selected_pages")

    with Session(engine) as session:

        document = session.get(
            Document,
            document_id,
        )

        if document is None:

            logger.error(
                f"Document {document_id} not found."
            )

            ch.basic_ack(
                delivery_tag=method.delivery_tag,
            )

            return

        document.status = DocumentStatus.processing

        session.add(document)
        session.commit()

        try:
            if selected_pages is None:
                logger.warning(
                    "No selected_pages provided in message for document %s; processing all pages.",
                    document.id,
                )
                selected_pages = list(range(1, document.pages + 1))

            service = AnalysisService(session)

            document_result = []

            for page_number in selected_pages:

                page_result = service.process_page(
                    document=document,
                    page_number=page_number,
                )

                document_result.append(
                    {
                        "page": page_number,
                        **page_result,
                    }
                )

            logger.info(document_result)

            ResultService(session).save_document_results(
            document=document,
            results=document_result,
                 )

            document.status = DocumentStatus.completed

        except Exception:

            logger.exception(
                f"Failed to process document {document.id}"
            )

            document.status = DocumentStatus.failed

        finally:

            session.add(document)
            session.commit()

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
        auto_ack=False,
    )

    logger.info("RabbitMQ worker started")

    channel.start_consuming()


if __name__ == "__main__":
    main()