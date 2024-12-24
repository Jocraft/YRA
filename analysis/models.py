from django.db import models

class Student(models.Model):
    def __str__(self):
        return self.name
