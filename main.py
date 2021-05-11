import os

from persian_clubhouse_ir.bot.bot import run_bot

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'persian_clubhouse_ir.settings')
    run_bot()
