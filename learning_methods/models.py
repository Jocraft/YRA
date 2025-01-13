from django.db import models
from accounts.models import Student

class LearningStyleTest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    
    # Answers for each question (1-16) - now storing multiple answers as comma-separated values
    q1 = models.CharField(max_length=10)  # Increased length to store multiple answers
    q2 = models.CharField(max_length=10)
    q3 = models.CharField(max_length=10)
    q4 = models.CharField(max_length=10)
    q5 = models.CharField(max_length=10)
    q6 = models.CharField(max_length=10)
    q7 = models.CharField(max_length=10)
    q8 = models.CharField(max_length=10)
    q9 = models.CharField(max_length=10)
    q10 = models.CharField(max_length=10)
    q11 = models.CharField(max_length=10)
    q12 = models.CharField(max_length=10)
    q13 = models.CharField(max_length=10)
    q14 = models.CharField(max_length=10)
    q15 = models.CharField(max_length=10)
    q16 = models.CharField(max_length=10)
    
    # VARK scores
    visual_score = models.IntegerField()
    aural_score = models.IntegerField()
    read_write_score = models.IntegerField()
    kinesthetic_score = models.IntegerField()

    class Meta:
        ordering = ['-date_taken']
    
   
       
    def __str__(self):
        return f"{self.student} - {self.date_taken.strftime('%Y-%m-%d %H:%M')}"
    @classmethod
    def get_tested_students_count(cls):
        return cls.objects.values('student').distinct().count()