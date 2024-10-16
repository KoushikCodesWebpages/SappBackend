# management/commands/import_data.py
from general.importers.csv_importer import import_csv_to_model
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Import data from a CSV file into a specified model'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='The app where the model is located')
        parser.add_argument('model_name', type=str, help='The model to import data into')
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        app_name = kwargs['app_name']
        model_name = kwargs['model_name']
        csv_file = kwargs['csv_file']

        # Dynamically load the model from the given app and model name
        try:
            model = apps.get_model(app_name, model_name)
        except LookupError:
            self.stderr.write(self.style.ERROR(f'Model "{model_name}" not found in app "{app_name}".'))
            return

        # Import CSV data using the csv_importer function
        try:
            created_count, skipped_count = import_csv_to_model(model, csv_file)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} records.'))
            self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} records (already existed).'))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File "{csv_file}" not found.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error during import: {str(e)}'))
