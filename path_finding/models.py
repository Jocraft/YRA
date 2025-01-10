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
    
    # Store answers for each question
    q1_numbers = models.CharField(max_length=255, blank=True, verbose_name="Working with numbers preference")
    q2_math = models.CharField(max_length=255, blank=True, verbose_name="Mathematical abilities")
    q3_problem_solving = models.CharField(max_length=255, blank=True, verbose_name="Problem solving approach")
    q4_future_job = models.TextField(blank=True, verbose_name="Future job preference")
    q5_tools = models.CharField(max_length=255, blank=True, verbose_name="Preferred tools")
    q6_tech_interest = models.CharField(max_length=255, blank=True, verbose_name="Technology interests")
    q7_learning = models.CharField(max_length=255, blank=True, verbose_name="Learning preference")
    q8_computer_skills = models.CharField(max_length=255, blank=True, verbose_name="Computer skills level")
    q9_projects = models.CharField(max_length=255, blank=True, verbose_name="Project interests")
    q10_goals = models.TextField(blank=True, verbose_name="Educational goals")
    
    # Store LLM analysis results
    llm_analysis = models.TextField(blank=True, verbose_name="Career Analysis Results")
    
    def __str__(self):
        return f"TestSession #{self.id} for {self.student}"

    class Meta:
        ordering = ["-date_taken"]

    @classmethod
    def get_tested_students_count(cls):
        """Returns the number of unique students who have taken the test"""
        return cls.objects.filter(is_complete=True).values('student').distinct().count()

class TestAnswer(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='test_answers')
    question_id = models.PositiveIntegerField()
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer {self.id} (Session {self.test_session_id})"
