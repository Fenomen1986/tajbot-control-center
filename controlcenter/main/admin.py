from django.contrib import admin
from django.utils.html import format_html
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
    readonly_fields = ('api_auth_token',) 

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'bot', 'colored_status', 'created_at') # 'status' заменен на 'colored_status'
    list_filter = ('status', 'bot')
    search_fields = ('customer_name', 'customer_data')
    ordering = ('-created_at',)
    readonly_fields = ('bot', 'customer_name', 'customer_data', 'created_at') 
    list_editable = ('status',) # Оставим возможность редактировать 'status', хотя он не отображается

    # --- НОВЫЙ КОД ДЛЯ ЦВЕТОВОГО КОДИРОВАНИЯ ---
    @admin.display(description='Статус')
    def colored_status(self, obj):
        if obj.status == 'Новая':
            color = 'green'
            text_color = 'white'
        elif obj.status == 'В работе':
            color = 'orange'
            text_color = 'white'
        else:
            color = 'transparent'
            text_color = 'inherit'
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 5px 10px; border-radius: 5px;">{}</span>',
            color,
            text_color,
            obj.get_status_display(),
        )
    
    # Добавляем 'status' в list_editable, чтобы его можно было редактировать.
    # Django достаточно умен, чтобы связать это с `colored_status`.
    list_display_links = ('customer_name',)