from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Cleanup expired password verification codes from sessions'

    def handle(self, *args, **options):
        expired_time = timezone.now() - timedelta(hours=24)
        expired_sessions = Session.objects.filter(expire_date__lt=expired_time)
    
        count = expired_sessions.count()
        expired_sessions.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired password verification sessions')
        )
