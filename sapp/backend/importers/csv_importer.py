import csv
from django.apps import apps

def import_csv_to_model(model_name, csv_file_path):
    try:
        # Get the model class from the provided model name
        model = apps.get_model('backend', model_name)
        
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Adjust this based on the fields of the specific model
                fields = {field: value for field, value in row.items() if value}
                if not model.objects.filter(**fields).exists():
                    model.objects.create(**fields)
                    print(f'{model_name} created with data: {fields}')
                else:
                    print(f'{model_name} already exists with data: {fields}')
    except Exception as e:
        print(f'Error: {str(e)}')
