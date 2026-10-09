from django.core.management.base import BaseCommand, CommandError
from books.services.audit import issues


class Command(BaseCommand):
    help = "Read-only circulation audit; never guesses historical readers."
    def add_arguments(self, parser): parser.add_argument("--dry-run",action="store_true")
    def handle(self,*args,**options):
        found=list(issues())
        for issue in found: self.stdout.write(issue)
        if found: raise CommandError(f"{len(found)} issues require review.")
        self.stdout.write("No structural issues. Historical reader identity was not verified.")