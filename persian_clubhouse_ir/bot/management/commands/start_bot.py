from django.core.management.base import BaseCommand

from persian_clubhouse_ir.bot.telegram_bot import run_bot


class Command(BaseCommand):
    help = 'Start telegram Bot'

    def handle(self, *args, **options):
        run_bot()
