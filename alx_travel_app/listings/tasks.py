"""
Celery tasks for the listings app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_data):
    """
    Celery task to send a booking confirmation email asynchronously.

    Args:
        booking_data (dict): Dictionary containing booking information
            - user_email: Email address of the user
            - booking_reference: Unique booking reference
            - property_name: Name of the property
            - check_in_date: Check-in date
            - check_out_date: Check-out date
            - total_price: Total price of the booking

    Returns:
        str: Success message if email is sent successfully
    """
    try:
        user_email = booking_data.get('user_email')
        booking_reference = booking_data.get('booking_reference')
        property_name = booking_data.get('property_name')
        check_in_date = booking_data.get('check_in_date')
        check_out_date = booking_data.get('check_out_date')
        total_price = booking_data.get('total_price')

        subject = f'Booking Confirmation - {booking_reference}'
        message = f"""
        Dear Customer,

        Thank you for your booking!

        Booking Details:
        ----------------
        Booking Reference: {booking_reference}
        Property: {property_name}
        Check-in Date: {check_in_date}
        Check-out Date: {check_out_date}
        Total Price: ${total_price}

        We look forward to hosting you!

        Best regards,
        ALX Travel App Team
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(f"Booking confirmation email sent to {user_email} for booking {booking_reference}")
        return f"Email sent successfully to {user_email}"

    except Exception as exc:
        logger.error(f"Error sending booking confirmation email: {str(exc)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
