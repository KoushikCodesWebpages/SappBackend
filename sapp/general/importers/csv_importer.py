# importer/csv_importer.py

import csv

def import_csv_to_model(model, csv_file_path):
    """
    Imports data from a CSV file into the specified model.
    
    Args:
        model: The Django model class where data will be imported.
        csv_file_path: The path to the CSV file.
        
    Returns:
        A summary of how many records were created and skipped.
    """
    created_count = 0
    skipped_count = 0

    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Attempt to create a new object or skip if it already exists
                obj, created = model.objects.get_or_create(**row)
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

    except FileNotFoundError:
        raise FileNotFoundError(f'CSV file "{csv_file_path}" not found.')

    except Exception as e:
        raise Exception(f'Error while importing CSV: {str(e)}')

    return created_count, skipped_count
