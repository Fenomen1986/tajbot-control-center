from django.db import models

class Client(models.Model):
    """Модель для хранения наших клиентов."""
    
    PLAN_CHOICES = (
        ('Базовый', 'Базовый'),
        ('Стандарт', 'Стандарт'),
        ('Премиум', 'Премиум'),
        ('Не активна', 'Не активна'),
    )

    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    contact_person = models.CharField(max_length=200, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=50, verbose_name="Телефон")
    
    subscription_plan = models.CharField(
        max_length=50, 
        choices=PLAN_CHOICES, 
        default='Не активна', 
        verbose_name="Тариф поддержки"
    )
    subscription_end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Подписка активна до"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.company_name

class Bot(models.Model):
    """Модель для хранения ботов, привязанных к клиентам."""
    
    PLATFORM_CHOICES = (
        ('Telegram', 'Telegram'),
        ('WhatsApp', 'WhatsApp'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bots', verbose_name="Клиент")
    name = models.CharField(max_length=100, verbose_name="Имя бота")
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, verbose_name="Платформа")
    token = models.CharField(max_length=255, verbose_name="API Токен (бота)") 
    # Этот токен мы будем использовать для связи бота с нашей системой
    api_auth_token = models.CharField(max_length=255, verbose_name="Токен авторизации API (системный)", unique=True)

    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Боты"

    def __str__(self):
        return f"{self.name} ({self.client.company_name})"

class Lead(models.Model):
    """Модель для хранения заявок (лидов), полученных от ботов."""

    STATUS_CHOICES = (
        ('Новая', 'Новая'),
        ('В работе', 'В работе'),
        ('Завершена', 'Завершена'),
        ('Отклонена', 'Отклонена'),
    )

    bot = models.ForeignKey(Bot, on_delete=models.SET_NULL, null=True, related_name='leads', verbose_name="Бот")
    customer_name = models.CharField(max_length=200, verbose_name="Имя клиента")
    customer_data = models.TextField(verbose_name="Данные заявки (телефон, бизнес, задача)")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Новая', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата поступления")
    
    class Meta:
        verbose_name = "Заявка (Лид)"
        verbose_name_plural = "Заявки (Лиды)"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.customer_name} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"