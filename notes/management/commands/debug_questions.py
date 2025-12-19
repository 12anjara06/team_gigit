from django.core.management.base import BaseCommand
from notes.models import Question

class Command(BaseCommand):
    help = 'Debug questions data'

    def handle(self, *args, **options):
        questions = Question.objects.all().select_related('user')
        self.stdout.write(f"Total questions: {questions.count()}")
        for q in questions:
            self.stdout.write(f"ID: {q.id}, User: {q.user.username if q.user else 'None'}, Content: {q.content[:50]}...")
