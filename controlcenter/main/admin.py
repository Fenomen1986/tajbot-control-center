from django.contrib import admin
from .models import Client, Bot, Lead

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'phone', 'subscription_plan', 'subscription_end_date')
    list_filter = ('subscription_plan',)
    search_fields = ('company_name', 'contact_person')
    ordering = ('company_name',)

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'platform')
    list_filter = ('platform', 'client')
    search_fields = ('name', 'client__company_name')
    # Делаем системный токен "только для чтения", чтобы его нельзя было случайно изменить
    readonly_fields = ('api_auth_token',) 

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'bot', 'status', 'created_at')
    list_filter = ('status', 'bot')
    search_fields = ('customer_name', 'customer_data')
    ordering = ('-created_at',)
    # Запрещаем редактирование заявок, их можно только просматривать и менять статус
    readonly_fields = ('bot', 'customer_name', 'customer_data', 'created_at') 
    list_editable = ('status',)