from django.db import models
from accounts.models import Student

class Program(models.Model):
    """
    Represents an academic program that can be recommended to students
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TestSession(models.Model):
    """
    Stores a record of a student's attempt at the career path test.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

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
