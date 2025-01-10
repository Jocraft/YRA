from django.core.management.base import BaseCommand
from path_finding.models import Question, Program

class Command(BaseCommand):
    help = 'Loads initial questions and programs data'

    def handle(self, *args, **kwargs):
        # Create example questions
        questions = [
            {
                'text': 'What subjects do you enjoy most in school and why?',
                'order': 1
            },
            {
                'text': 'Describe your ideal work environment and the type of tasks you would enjoy doing.',
                'order': 2
            },
            {
                'text': 'What are your favorite hobbies or activities outside of school?',
                'order': 3
            },
            {
                'text': 'Where do you see yourself in 10 years? Describe your ideal career.',
                'order': 4
            },
            {
                'text': 'What skills or talents do others often compliment you on?',
                'order': 5
            }
        ]

        # Create example programs
        programs = [
            {
                'name': 'Computer Science',
                'description': 'Study of computers and computational systems, including programming, software development, and computer theory.',
                'keywords': 'technology, programming, software, computers, mathematics, logic, problem-solving'
            },
            {
                'name': 'Business Administration',
                'description': 'Study of business operations, management, marketing, and entrepreneurship.',
                'keywords': 'management, business, marketing, leadership, entrepreneurship, finance'
            },
            {
                'name': 'Mechanical Engineering',
                'description': 'Design and manufacturing of mechanical systems and machines.',
                'keywords': 'engineering, mechanics, design, manufacturing, physics, mathematics'
            },
            {
                'name': 'Psychology',
                'description': 'Study of human behavior, mental processes, and counseling.',
                'keywords': 'behavior, mental health, counseling, research, human development'
            },
            {
                'name': 'Graphic Design',
                'description': 'Visual communication and digital art creation.',
                'keywords': 'design, art, creativity, digital media, visual communication'
            }
        ]

        # Clear existing data
        Question.objects.all().delete()
        Program.objects.all().delete()

        # Create new questions
        for q in questions:
            Question.objects.create(text=q['text'], order=q['order'])
            self.stdout.write(f"Created question: {q['text'][:50]}...")

        # Create new programs
        for p in programs:
            Program.objects.create(
                name=p['name'],
                description=p['description'],
                keywords=p['keywords']
            )
            self.stdout.write(f"Created program: {p['name']}")

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data')) 