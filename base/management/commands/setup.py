import environ
from django.core.management.base import BaseCommand
from django.conf import settings
import MySQLdb
from audit.models import Question_type
from django.contrib.auth.models import Group  # Import the Group model

env = environ.Env()
environ.Env.read_env()

class Command(BaseCommand):
    help = 'Sets up the database, runs migrations, populates the Question_type table, and creates an Analyst user group.'

    def handle(self, *args, **kwargs):
        # Debugging: Check environment variable values
        db_engine = env('DB_ENGINE').strip()
        db_name = env('DB_NAME', default='not_set')
        db_host = env('DB_HOST', default='not_set')
        db_port = env('DB_PORT', default='3306')
        db_user = env('DB_USER', default='not_set')
        db_password = env('DB_PASSWORD', default='not_set')
        
        # Print to see if the environment values are correct
        print(f"DB_ENGINE: {db_engine}")
        
        if db_engine == 'mysql':
            try:
                # Connect to MySQL server without specifying the database
                connection = MySQLdb.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    port=int(db_port),
                )
                connection.autocommit(True)
                cursor = connection.cursor()

                # Create the database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' created or already exists."))
            except MySQLdb.Error as e:
                self.stdout.write(self.style.ERROR(f"Error creating database: {e}"))
                return
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'connection' in locals():
                    connection.close()

        elif db_engine == 'sqlite3':
            self.stdout.write(self.style.SUCCESS(f"Using SQLite database '{db_name}'."))

        else:
            self.stdout.write(self.style.ERROR(f"Unsupported DB_ENGINE: {db_engine}"))
            return

        # Now run migrations using Django's connection (after the DB is created)
        settings.DATABASES['default']['NAME'] = db_name
        from django.core.management import call_command
        call_command('migrate')

        # Populate the Question_type table
        question_types = [
            'Range',
            'Likert10N',
            'Likert10',
            'Likert7N',
            'Likert7',
            'Likert5N',
            'Likert5',
            'Likert3N',
            'Likert3',
            'BoolP',
            'BoolN',
            'Time'
        ]

        for qt in question_types:
            Question_type.objects.get_or_create(type=qt)

        self.stdout.write(self.style.SUCCESS("Question_type table has been populated successfully."))

        # Create the Analyst user group
        analyst_group, created = Group.objects.get_or_create(name='Analyst')
        if created:
            self.stdout.write(self.style.SUCCESS("Analyst user group has been created."))
        else:
            self.stdout.write(self.style.SUCCESS("Analyst user group already exists."))
