import csv
from django.core.management.base import BaseCommand
from backend.models import Standard

class Command(BaseCommand):
    help = 'Import standards from a CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = 'data\standards.csv'  # Update with the path to your CSV file
        try:
            with open(csv_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    standard_name = row['name']
                    if not Standard.objects.filter(name=standard_name).exists():
                        Standard.objects.create(name=standard_name)
                        self.stdout.write(self.style.SUCCESS(f'Standard "{standard_name}" created'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Standard "{standard_name}" already exists'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
