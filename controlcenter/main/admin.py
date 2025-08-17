from django.contrib import admin
from .models import Client, Bot, Lead

# Мы снова используем стандартный admin.site

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    # ... (весь код ClientAdmin остается без изменений)
    list_display = ('company_name', 'contact_person', 'phone', 'subscription_plan', 'subscription_end_date')
    list_filter = ('subscription_plan',)
    search_fields = ('company_name', 'contact_person')
    ordering = ('company_name',)

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    # ... (весь код BotAdmin остается без изменений)
    list_display = ('name', 'client', 'platform')
    list_filter = ('platform', 'client')
    search_fields = ('name', 'client__company_name')
    readonly_fields = ('api_auth_token',) 

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    # ... (весь код LeadAdmin остается без изменений)
    list_display = ('customer_name', 'bot', 'status', 'created_at')
    list_filter = ('status', 'bot')
    search_fields = ('customer_name', 'customer_data')
    ordering = ('-created_at',)
    readonly_fields = ('bot', 'customer_name', 'customer_data', 'created_at') 
    list_editable = ('status',)