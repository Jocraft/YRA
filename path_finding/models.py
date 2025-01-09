from django.db import models
from accounts.models import Student  # <-- import your Student model here

class TestSession(models.Model):
    """
    Stores a record of a student's attempt at the career path test.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    
    # If you want to store answers in JSON (requires Django 3.1+):
    # answers = models.JSONField(null=True, blank=True)
    #
    # Or create another model TestAnswer, referencing this TestSession.

    def __str__(self):
        return f"TestSession #{self.id} for {self.student}"

    class Meta:
        ordering = ["-date_taken"]
class TestAnswer(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='test_answers')
    question_id = models.PositiveIntegerField()
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer {self.id} (Session {self.test_session_id})"
