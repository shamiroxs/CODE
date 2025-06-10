from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Runs migrate and collectstatic on Render'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Running migrate..."))
        call_command('migrate', interactive=False)
        self.stdout.write(self.style.SUCCESS("Running collectstatic..."))
        call_command('collectstatic', interactive=False, verbosity=0)
        self.stdout.write(self.style.SUCCESS("Setup complete!"))
