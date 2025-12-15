import logging
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def extract_and_rank_resume(application_id: int) -> str:
    """
    Extract resume text and rerank applications synchronously.

    Args:
        application_id: ID of the application to process

    Returns:
        Status message
    """
    from .models import Application
    from .services import extract_resume_text, rerank_applications

    try:
        logger.info("Starting resume extraction for application %s", application_id)

        application = Application.objects.select_related("job").get(pk=application_id)

        resume_text = extract_resume_text(application.resume)

        with transaction.atomic():
            application.resume_text = resume_text
            application.save(update_fields=["resume_text"])

        logger.info("Resume text extracted for application %s", application_id)

        rerank_applications(application.job)

        logger.info("Successfully processed application %s", application_id)
        return f"Application {application_id} processed successfully"

    except Application.DoesNotExist:
        logger.error("Application %s not found", application_id)
        return f"Application {application_id} not found"

    except Exception as exc:
        logger.exception(
            "Unexpected error while processing application %s", application_id
        )
        raise exc
