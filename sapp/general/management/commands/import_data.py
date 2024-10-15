from django.core.management.base import BaseCommand
from backend.importers.csv_importer import import_csv_to_model

class Command(BaseCommand):
    help = 'Import data from a CSV file into the specified model'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='Name of the model to import data into')
        parser.add_argument('csv_file', type=str, help='Path to the CSV file to import')

    def handle(self, *args, **kwargs):
        model_name = kwargs['model_name']
        csv_file_path = kwargs['csv_file']

        import_csv_to_model(model_name, csv_file_path)
