from django.core.management.base import BaseCommand
from django.conf import settings
import telebot

class Command(BaseCommand):
    help = 'Sets the Telegram webhook for the bot.'

    def handle(self, *args, **options):
        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
        
        # URL нашего приложения на Railway
        webhook_url_base = "https://tajbot-control-center-production.up.railway.app" # Убедитесь, что это ваш правильный домен
        webhook_url_path = f"/api/webhook/{settings.TELEGRAM_BOT_TOKEN}/"
        
        full_webhook_url = webhook_url_base + webhook_url_path
        
        self.stdout.write(f"Setting webhook to: {full_webhook_url}")
        
        try:
            bot.remove_webhook()
            bot.set_webhook(url=full_webhook_url)
            self.stdout.write(self.style.SUCCESS('Webhook has been set successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to set webhook: {e}'))