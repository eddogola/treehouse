from django.core.management.base import BaseCommand, CommandError

from main.models import Role

class Command(BaseCommand):
    help = 'Inserts roles 1(Founder),2(Admin) & 3(Regular)'

    def handle(self, *args, **kwargs):
        roles = ((1, 'Founder'), (2, 'Admin'), (3, 'Regular'))
        for role in roles:
            try:
                Role.objects.create(role=role[0])
                self.stdout.write(
                    self.style.SUCCESS('Successfully installed role {}'.format(role)))
            except CommandError:
                self.stderr.write(self.style.ERROR('an error occured'))
        