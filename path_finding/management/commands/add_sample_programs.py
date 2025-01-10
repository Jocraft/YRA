from django.core.management.base import BaseCommand
from path_finding.models import Program

class Command(BaseCommand):
    help = 'Adds sample programs to the database'

    def handle(self, *args, **kwargs):
        SAMPLE_PROGRAMS = [
            {
                'name': 'Computer Science',
                'description': 'Study of computation, programming, and information systems. Focus on software development, algorithms, and computer theory.'
            },
            # ... other programs ...
        ]

        for program in SAMPLE_PROGRAMS:
            Program.objects.get_or_create(
                name=program['name'],
                defaults={'description': program['description']}
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample programs')) 