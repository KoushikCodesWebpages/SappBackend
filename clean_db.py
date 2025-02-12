import os
import shutil
import subprocess

# Define paths
paths_to_clean = [
    "sapp/accounts/migrations",
    "sapp/features/migrations"
]

# Files and directories to exclude
excluded_files = {"__init__.py"}
excluded_dirs = {"__pycache__"}

def clean_migrations():
    """Delete all migration files except '__init__.py'."""
    for path in paths_to_clean:
        if os.path.exists(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and item not in excluded_files:
                    os.remove(item_path)
                elif os.path.isdir(item_path) and item not in excluded_dirs:
                    shutil.rmtree(item_path)
    print("✅ Migrations cleaned.")

def delete_db():
    """Delete the SQLite database file."""
    db_path = "db.sqlite3"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Deleted: {db_path}")
    else:
        print("⚠️ Database file not found, skipping.")

def run_django_commands():
    """Run Django migration and server commands."""
    commands = [
        ["python", "sapp/manage.py", "makemigrations"],
        ["python", "sapp/manage.py", "migrate"],
        ["python", "sapp/manage.py", "runserver"]
    ]
    
    for command in commands:
        print(f"▶️ Running: {' '.join(command)}")
        process = subprocess.run(command)
        if process.returncode != 0:
            print(f"❌ Error running: {' '.join(command)}")
            break

# Execute the process
clean_migrations()
delete_db()
run_django_commands()
