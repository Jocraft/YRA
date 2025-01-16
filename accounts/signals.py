from .utils import (
    generate_student_credentials,
    generate_lecturer_credentials,
    send_new_account_email,
)


def post_save_account_receiver(instance=None, created=False, *args, **kwargs):
    """
    Send email notification and update username/password with 
    the newly generated credentials if a student or lecturer is created.
    """
    if created:
        if instance.is_student:
            # 1) Generate a unique Student ID + random password
            username, password = generate_student_credentials()
            # 2) Assign them to the new user
            instance.username = username
            instance.set_password(password)
            instance.save()
            # 3) Send an email with the credentials
            send_new_account_email(instance, password)

        if instance.is_lecturer:
            # 1) Generate a unique Lecturer ID + random password
            username, password = generate_lecturer_credentials()
            # 2) Assign them to the new user
            instance.username = username
            instance.set_password(password)
            instance.save()
            # 3) Send an email with the credentials
            send_new_account_email(instance, password)
