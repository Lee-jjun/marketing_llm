from django.core.management.base import BaseCommand
from apps.data.models import Review
import csv

class Command(BaseCommand):
    help = 'Ingest reviews from csv'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str)

    def handle(self, *args, **options):
        path = options['csvfile']
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                Review.objects.create(
                    original_text=r['text'],
                    metadata={'source': r.get('source')}
                )
        self.stdout.write(self.style.SUCCESS('Ingest completed'))