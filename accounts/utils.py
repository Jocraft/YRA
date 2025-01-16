import threading
import uuid
from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings
from core.utils import send_html_email


def generate_password():
    """Generates a random password using Django's built-in password generator."""
    return get_user_model().objects.make_random_password()


def generate_student_id():
    """
    Generate a unique Student ID using a UUID-based approach (no .count()).

    Example output: STU-2025-A1B2C3
    (assuming settings.STUDENT_ID_PREFIX == "STU")
    """
    registered_year = datetime.now().strftime("%Y")
    random_hex = uuid.uuid4().hex[:6].upper()  # 6-char random hex (e.g. 'A1B2C3')
    return f"{settings.STUDENT_ID_PREFIX}-{registered_year}-{random_hex}"


def generate_lecturer_id():
    """
    Generate a unique Lecturer ID using a UUID-based approach (no .count()).

    Example output: LEC-2025-D4E5F6
    (assuming settings.LECTURER_ID_PREFIX == "LEC")
    """
    registered_year = datetime.now().strftime("%Y")
    random_hex = uuid.uuid4().hex[:6].upper()
    return f"{settings.LECTURER_ID_PREFIX}-{registered_year}-{random_hex}"


def generate_student_credentials():
    """
    Return (unique_student_id, random_password).
    Called by signals.py when creating a new student.
    """
    return generate_student_id(), generate_password()


def generate_lecturer_credentials():
    """
    Return (unique_lecturer_id, random_password).
    Called by signals.py when creating a new lecturer.
    """
    return generate_lecturer_id(), generate_password()


class EmailThread(threading.Thread):
    """
    Utility for sending HTML email in a background thread.
    """
    def __init__(self, subject, recipient_list, template_name, context):
        self.subject = subject
        self.recipient_list = recipient_list
        self.template_name = template_name
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        send_html_email(
            subject=self.subject,
            recipient_list=self.recipient_list,
            template=self.template_name,
            context=self.context,
        )


def send_new_account_email(user, password):
    """
    Sends a 'new account credentials' email to the user.
    """
    if user.is_student:
        template_name = "accounts/email/new_student_account_confirmation.html"
    else:
        template_name = "accounts/email/new_lecturer_account_confirmation.html"
    email = {
        "subject": "Your SkyLearn account confirmation and credentials",
        "recipient_list": [user.email],
        "template_name": template_name,
        "context": {"user": user, "password": password},
    }
    EmailThread(**email).start()
