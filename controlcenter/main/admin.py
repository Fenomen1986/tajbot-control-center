from django.contrib import admin
from .models import Client, Bot, Lead

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'phone', 'subscription_plan', 'subscription_end_date')

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'platform')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'bot', 'status', 'created_at')